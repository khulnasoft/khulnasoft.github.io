"""Engineering data lake and event ingestion.

Raw signals (GitHub, GitLab, CI/CD, Kubernetes, cloud, monitoring, security,
packages, documentation, and AI sources) are normalized into a versioned event
store under `data/events/`. The data lake keeps raw events separate from
normalized state, so derived layers (twins, graph, context, intelligence) can
be refreshed selectively when events land.

Source-specific adapters (`github_to_event`, `gitlab_to_event`, ...) translate
raw webhook payloads into canonical events so any system can publish to the
control plane using its native format. The webhook handler in serve_api.py
routes by source and persists accepted events via `persist_event`.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

EVENT_DIR = ROOT / "data" / "events"

# Deterministic influence of each event type on a resource's health score.
HEALTH_EFFECTS = {
    "repository.push": 0,
    "repository.commit": 0,
    "workflow.run": 0,
    "ci.run": 0,
    "deployment.success": 2,
    "deployment.failure": -8,
    "deployment.rollback": -3,
    "security.findings": -6,
    "security.policy_violation": -5,
    "health.degraded": -7,
    "health.recovered": 5,
    "dependency.update": 1,
    "dependency.vulnerable": -4,
    "incident.triggered": -10,
    "release.published": 3,
    "package.published": 1,
    "doc.updated": 0,
    "ai.run": 0,
}

SUPPORTED_SOURCES = {"github", "gitlab", "ci", "kubernetes", "cloud", "monitoring", "security", "custom",
                     "packages", "documentation", "ai"}


def load_events(events_dir: Path | None = None) -> list[dict]:
    """Load and normalize every event in the event store, deduplicated by id.

    Both single-object files and arrays (batched ingestion) are supported so
    the data lake stays extensible.
    """
    events_dir = events_dir or EVENT_DIR
    normalized: list[dict] = []
    if not events_dir.exists():
        return normalized
    for path in sorted(events_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            evt = normalize_event(item)
            if evt is not None:
                normalized.append(evt)
    by_id: dict[str, dict] = {}
    for evt in normalized:
        by_id[evt["id"]] = evt
    return [by_id[k] for k in sorted(by_id)]


def normalize_event(raw: dict) -> dict | None:
    """Validate and normalize a raw signal into a canonical event."""
    evt_id = raw.get("id")
    etype = raw.get("type")
    if not evt_id or not etype:
        return None
    source = raw.get("source", "custom")
    if source not in SUPPORTED_SOURCES:
        source = "custom"
    scope = raw.get("scope") or []
    scope = [s for s in scope if isinstance(s, str)]
    return {
        "id": evt_id,
        "source": source,
        "type": etype,
        "happenedAt": raw.get("happenedAt", "unknown"),
        "scope": scope,
        "payload": raw.get("payload", {}),
    }


def persist_event(raw: dict, events_dir: Path | None = None) -> dict:
    """Accept a (possibly raw, source-specific) event, normalize it, and append
    it to the versioned event store so the next build ingests it for targeted
    refresh.

    Returns the normalized event that was persisted.
    """
    events_dir = events_dir or EVENT_DIR
    events_dir.mkdir(parents=True, exist_ok=True)
    canonical = normalize_event(raw)
    if canonical is None:
        raise ValueError("event must have id and type")
    path = events_dir / f"{canonical['id']}.json"
    path.write_text(json.dumps(canonical, indent=2, ensure_ascii=False), encoding="utf-8")
    return canonical


# ---------------------------------------------------------------------------
# Source adapters: translate raw webhook/payload formats into canonical events.
# These are pure and idempotent; the API/webhook layer routes by source header.
# ---------------------------------------------------------------------------


def _canonical(raw: dict, source: str, etype: str, scope: list[str], payload: dict,
               happened: str | None = None) -> dict:
    return {
        "id": raw.get("id") or f"evt:{source}:{etype}:{uuid.uuid4().hex[:8]}",
        "source": source,
        "type": etype,
        "happenedAt": happened or raw.get("happenedAt", raw.get("created_at", "unknown")),
        "scope": [s for s in scope if isinstance(s, str)],
        "payload": payload,
    }


def github_to_event(payload: dict) -> dict | None:
    """Translate a GitHub webhook payload into a canonical event."""
    header = payload.get("headers", {})
    event = header.get("X-GitHub-Event") or payload.get("event")
    action = payload.get("action")
    repo = (payload.get("repository") or {}).get("full_name", "")
    slug = f"resource:{repo.replace('/', '-')}" if repo else None

    if event == "push":
        return _canonical(payload, "github", "repository.push", [slug] if slug else [],
                          {"ref": payload.get("ref"), "commits": len(payload.get("commits", [])),
                           "repository": repo},
                          happened=payload.get("head_commit", {}).get("timestamp"))
    if event == "workflow_run" and action == "completed":
        name = payload.get("workflow_run", {}).get("name")
        conclusion = payload.get("workflow_run", {}).get("conclusion")
        return _canonical(payload, "ci", "workflow.run", [slug] if slug else [],
                          {"workflow": name, "conclusion": conclusion, "repository": repo},
                          happened=payload.get("workflow_run", {}).get("updated_at"))
    if event == "issues" and action == "opened":
        return _canonical(payload, "github", "repository.issue", [slug] if slug else [],
                          {"number": payload.get("issue", {}).get("number"),
                           "repository": repo},
                          happened=payload.get("issue", {}).get("created_at"))
    if event == "release" and action == "published":
        return _canonical(payload, "github", "release.published", [slug] if slug else [],
                          {"tag": payload.get("release", {}).get("tag_name"), "repository": repo},
                          happened=payload.get("release", {}).get("published_at"))
    return None


def gitlab_to_event(payload: dict) -> dict | None:
    """Translate a GitLab webhook payload into a canonical event."""
    header = payload.get("headers", {})
    event = header.get("X-Gitlab-Event", "").lower()
    object_kind = (payload.get("object_kind") or "").lower()
    project = (payload.get("project") or {}).get("path_with_namespace", "")
    slug = f"resource:{project.replace('/', '-')}" if project else None

    if object_kind == "push" or event.startswith("push"):
        return _canonical(payload, "gitlab", "repository.push", [slug] if slug else [],
                          {"ref": payload.get("ref"), "commits": payload.get("total_commits_count", 0),
                           "project": project},
                          happened=payload.get("commits") and payload["commits"][0].get("timestamp"))
    if object_kind == "pipeline":
        return _canonical(payload, "ci", "workflow.run", [slug] if slug else [],
                          {"status": payload.get("object_attributes", {}).get("status"),
                           "project": project},
                          happened=payload.get("object_attributes", {}).get("created_at"))
    return None


def kubernetes_to_event(payload: dict) -> dict | None:
    """Translate a Kubernetes (deployment/status) payload into a canonical event."""
    kind = (payload.get("kind") or "").lower()
    meta = payload.get("metadata", {})
    name = meta.get("name")
    ns = meta.get("namespace", "default")
    slug = f"resource:{name}" if name else None
    if kind == "deployment":
        status = (payload.get("status", {}) or {})
        ready = status.get("readyReplicas", 0)
        unavailable = status.get("unavailableReplicas", 0)
        etype = "deployment.success" if not unavailable else "deployment.failure"
        return _canonical(payload, "kubernetes", etype, [slug] if slug else [],
                          {"namespace": ns, "ready": ready, "unavailable": unavailable},
                          happened=meta.get("creationTimestamp"))
    if kind == "event":
        reason = payload.get("reason", "").lower()
        etype = "deployment.failure" if "fail" in reason else "health.degraded"
        return _canonical(payload, "kubernetes", etype, [slug] if slug else [],
                          {"reason": reason, "namespace": ns},
                          happened=meta.get("creationTimestamp"))
    return None


def cloud_to_event(payload: dict) -> dict | None:
    """Translate a cloud-provider event payload into a canonical event."""
    source = payload.get("source", "")
    etype = payload.get("type", "")
    slug = payload.get("resource") or payload.get("resourceId")
    eff = "deployment.failure" if "fail" in etype.lower() or "degrad" in etype.lower() else "deployment.success"
    if not etype:
        return None
    return _canonical(payload, "cloud", eff, [slug] if slug else [],
                      {"source": source, "detail": payload.get("detail", {})},
                      happened=payload.get("time"))


def monitoring_to_event(payload: dict) -> dict | None:
    """Translate a monitoring alert payload into a canonical event."""
    status = (payload.get("status", "")).lower()
    if status == "firing":
        etype = "health.degraded"
    elif status == "resolved":
        etype = "health.recovered"
    else:
        etype = payload.get("type", "")
    if not etype:
        return None
    slug = payload.get("resource") or payload.get("labels", {}).get("resource")
    return _canonical(payload, "monitoring", etype, [slug] if slug else [],
                      {"alertname": payload.get("labels", {}).get("alertname"),
                       "severity": payload.get("labels", {}).get("severity"),
                       "value": payload.get("value")},
                      happened=payload.get("startsAt"))


def security_to_event(payload: dict) -> dict | None:
    """Translate a security finding payload into a canonical event."""
    repo = payload.get("repository") or payload.get("location", {}).get("file")
    slug = f"resource:{repo.replace('/', '-')}" if repo else payload.get("resource")
    findings = payload.get("vulnerabilities") or payload.get("findings") or []
    return _canonical(payload, "security", "security.findings", [slug] if slug else [],
                      {"count": len(findings), "findings": findings},
                      happened=payload.get("createdAt"))


def package_to_event(payload: dict) -> dict | None:
    """Translate a package-publish payload into a canonical event."""
    pkg = payload.get("package", {}).get("name") or payload.get("name")
    slug = f"resource:{pkg}" if pkg else None
    return _canonical(payload, "packages", "package.published", [slug] if slug else [],
                      {"package": pkg, "version": payload.get("version")},
                      happened=payload.get("published_at"))


def doc_to_event(payload: dict) -> dict | None:
    """Translate a documentation update payload into a canonical event."""
    slug = payload.get("resource") or payload.get("doc", {}).get("path", "").replace("/", "-")
    return _canonical(payload, "documentation", "doc.updated", [slug] if slug else [],
                      {"title": payload.get("doc", {}).get("title"), "path": payload.get("doc", {}).get("path")},
                      happened=payload.get("updatedAt"))


def ai_to_event(payload: dict) -> dict | None:
    """Translate an AI runtime event payload into a canonical event."""
    slug = payload.get("resource")
    etype = payload.get("type", "ai.run")
    return _canonical(payload, "ai", etype, [slug] if slug else [],
                      {"model": payload.get("model"), "tokens": payload.get("tokens"),
                       "latencyMs": payload.get("latencyMs")},
                      happened=payload.get("happenedAt"))


# Mapping of source name -> adapter, for webhook routing.
SOURCE_ADAPTERS = {
    "github": github_to_event,
    "gitlab": gitlab_to_event,
    "kubernetes": kubernetes_to_event,
    "cloud": cloud_to_event,
    "monitoring": monitoring_to_event,
    "security": security_to_event,
    "packages": package_to_event,
    "documentation": doc_to_event,
    "ai": ai_to_event,
}


def route_event(raw: dict, source: str | None = None) -> dict | None:
    """Route a raw payload to the adapter for `source`, or fall back to normalization."""
    src = (source or raw.get("source") or "").lower()
    adapter = SOURCE_ADAPTERS.get(src)
    if adapter:
        return adapter(raw)
    return normalize_event(raw)


def apply_events(resources: list[dict], events: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply event effects onto a copy of the resource registry.

    Returns (updated_resources, applied_events) where `applied_events` records
    each event with the concrete resource ids it touched. Health influence is
    deterministic and clamped to [0, 100]; nothing is mutated in place.
    """
    index = {r["id"]: json.loads(json.dumps(r)) for r in resources}
    applied: list[dict] = []
    for evt in events:
        effect = HEALTH_EFFECTS.get(evt["type"], 0)
        touched = [rid for rid in evt["scope"] if rid in index]
        if not touched and effect == 0:
            continue
        for rid in touched:
            health = index[rid].get("health", {})
            score = health.get("score", 80)
            health["score"] = max(0, min(100, score + effect))
            health.setdefault("status", "healthy")
            if health["score"] < 70:
                health["status"] = "degraded"
            index[rid]["health"] = health
            index[rid].setdefault("ingestionEvents", []).append(evt["id"])
        applied.append({**evt, "touched": touched, "healthEffect": effect})
    return [index[rid] for rid in sorted(index)], applied


def affected_index(events: list[dict]) -> dict:
    """Map each event to the resources it touches (for targeted refresh)."""
    return {evt["id"]: {"type": evt["type"], "touched": list(evt.get("scope", []))} for evt in events}


def summarize(events: list[dict], resources: list[dict]) -> dict:
    """Aggregate a data-lake summary for dashboards and the API."""
    by_type: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for evt in events:
        by_type[evt["type"]] = by_type.get(evt["type"], 0) + 1
        by_source[evt["source"]] = by_source.get(evt["source"], 0) + 1
    return {
        "total_events": len(events),
        "sources": by_source,
        "types": by_type,
        "resources_touched": len({rid for evt in events for rid in evt.get("scope", [])}),
    }

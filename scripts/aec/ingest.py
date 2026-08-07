"""Engineering data lake and event ingestion.

Raw signals (GitHub, CI, Kubernetes, cloud, monitoring, security) are
normalized into a versioned event store under `data/events/`. The data lake
keeps raw events separate from normalized state, so derived layers (twins,
graph, context, intelligence) can be refreshed selectively when events land.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

EVENT_DIR = ROOT / "data" / "events"

# Deterministic influence of each event type on a resource's health score.
HEALTH_EFFECTS = {
    "repository.push": 0,
    "deployment.success": 2,
    "deployment.failure": -8,
    "security.findings": -6,
    "health.degraded": -7,
    "health.recovered": 5,
    "dependency.update": 1,
    "incident.triggered": -10,
    "ci.run": 0,
    "release.published": 3,
}

SUPPORTED_SOURCES = {"github", "gitlab", "ci", "kubernetes", "cloud", "monitoring", "security", "custom"}


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

"""Intelligence plane analyzers.

Analyzers run over the resource registry at build time to surface engineering
intelligence: language/framework/architecture/API/security detection, dependency
resolution, technical debt, deprecation, and performance-regression signals.
Deterministic and derived — never hand-maintained.
"""
from __future__ import annotations

from typing import Iterable

# Canonical taxonomies used across analyzers.
LANGUAGES = {".ts": "typescript", ".py": "python", ".go": "go", ".rs": "rust", ".java": "java", ".cs": "csharp"}
FRAMEWORKS = ["fastapi", "node", "react", "next.js", "spring", "flask", "django", "gin", "actix"]
ARCH_PATTERNS = ["microservice", "serverless", "event-driven", "layered", "monolith"]
ARCH_ALIGNS = {
    "microservice": "microservice", "serverless": "function", "event-driven": "queue",
    "layered": "api", "monolith": "application",
}


def detect_languages(languages: list[str] | None, files: list[str] | None = None) -> list[str]:
    declared = languages or []
    ext = {LANGUAGES[e] for e in (files or []) if e in LANGUAGES}
    declared = list(dict.fromkeys([*declared, *ext]))
    return declared


def detect_frameworks(frameworks: list[str] | None, languages: list[str] | None = None) -> list[str]:
    frameworks = frameworks or []
    return list(dict.fromkeys(frameworks))


def resolve_dependencies(resource: dict) -> list[dict]:
    return [
        {"type": rel.get("type", "related"), "target": rel.get("target")}
        for rel in resource.get("relationships", [])
    ]


def detect_architecture(resource: dict) -> list[str]:
    stress_caps = [c.lower() for c in resource.get("capabilities", [])]
    found = [p for p in ARCH_PATTERNS if p in " ".join(stress_caps)]
    return found or ["layered"]


def detect_api(resource: dict) -> bool:
    return bool(resource.get("apis") or resource.get("exposes") or "api" in [c.lower() for c in resource.get("capabilities", [])])


def detect_security(resource: dict) -> dict:
    sec = resource.get("security", {})
    scan = sec.get("scanStatus", "unknown")
    posture = sec.get("posture", "unknown")
    return {
        "scanStatus": scan,
        "posture": posture,
        "clean": scan == "clean",
        "risk": "low" if scan == "clean" else ("medium" if scan == "unknown" else "high"),
    }


def tech_debt(resource: dict, readiness: dict) -> list[str]:
    debt = []
    scores = readiness.get("scores", {})
    if scores.get("documentation", 100) < 70:
        debt.append("documentation gap")
    if scores.get("tests", 100) < 70:
        debt.append("low test coverage")
    if scores.get("security", 100) < 70:
        debt.append("security debt")
    if resource.get("health", {}).get("drift"):
        debt.append("drift detected")
    if resource.get("health", {}).get("score", 100) < 70:
        debt.append("health below threshold")
    if scores.get("dependencies", 100) < 70:
        debt.append("dependency risk")
    return debt or ["none detected"]


def detect_deprecation(resource: dict) -> dict:
    lifecycle = resource.get("lifecycle", "active")
    deprecated = lifecycle == "deprecated"
    return {"deprecated": deprecated, "lifecycle": lifecycle}


def detect_perf_regression(resource: dict) -> dict:
    health = resource.get("health", {})
    obs = resource.get("observability", {})
    degraded = health.get("status") in ("degraded", "warning", "critical") or obs.get("p99", 0) > 400
    label = obs.get("p99_label") or (f"health {health.get('status')}" if degraded else None)
    return {"regression": bool(degraded), "signal": label}


# ---------------------------------------------------------------------------
# Phase 6.2 — additional engineering-intelligence analyzers.
# ---------------------------------------------------------------------------


def detect_api_compatibility(resource: dict) -> dict:
    """Surface API compatibility risk for resources exposing interfaces.

    A versioned API contract is required before an API can be surfaced to
    consumers; un-versioned APIs imply a compatibility risk.
    """
    exposes_api = resource.get("apis") or resource.get("exposes") or any(
        c.lower() == "api" for c in resource.get("capabilities", [])
    )
    if not exposes_api:
        return {"risk": "none", "versioned": False, "note": "resource does not expose an API"}
    versioned = bool(resource.get("version"))
    return {
        "risk": "unversioned" if not versioned else "none",
        "versioned": versioned,
        "note": "API must carry a version to guarantee compatibility" if not versioned else "API is versioned",
    }


def detect_migration_suggestions(resource: dict, resources_by_id: dict) -> list[str]:
    """Suggest a migration target for deprecated resources when a capable successor exists."""
    if resource.get("lifecycle") != "deprecated":
        return []
    caps = {c.lower() for c in resource.get("capabilities", [])}
    successors = []
    for r in resources_by_id.values():
        if r["id"] == resource["id"] or r.get("lifecycle") == "retired":
            continue
        rc = {c.lower() for c in r.get("capabilities", [])}
        if caps & rc and r.get("lifecycle") in ("supported", "stable", "active"):
            successors.append(r)
    suggestions = [f"Migrate to {s['name']} ({s['id']})" for s in successors[:3]]
    if not suggestions:
        suggestions.append("No direct successor found in the registry — plan a replacement.")
    return suggestions


def detect_cost_optimization(resource: dict, readiness: dict) -> list[str]:
    """Flag cost-optimization opportunities on deployed, low-readiness assets."""
    opts = []
    targets = resource.get("deployment", {}).get("targets", [])
    if targets and readiness.get("overall", 100) < 60:
        opts.append(f"Downgrade or re-evaluate {resource['deployment'].get('environment', 'this')} deployment — readiness {readiness.get('overall')} is below threshold")
    if resource.get("health", {}).get("score", 100) < 60 and targets:
        opts.append("Resource is unhealthy in a live deployment — investigate and right-size")
    if not resource.get("relationships"):
        opts.append("No incoming relationships — confirm the resource is still needed")
    return opts


def detect_unused_components(resource: dict, incoming: dict[str, int]) -> bool:
    """A component is unused when no other resource depends on it and it has no
    outbound relationships of its own (an orphan leaf)."""
    deps = {rel.get("target") for rel in resource.get("relationships", [])}
    return (not incoming.get(resource["id"], 0)) and (not deps)


def detect_duplicate_libraries(resources: list[dict]) -> dict:
    """Detect libraries with overlapping capabilities in the same workspace."""
    seen: dict[tuple, list[dict]] = {}
    for r in resources:
        if r["kind"] not in ("library", "sdk"):
            continue
        key = (r.get("workspace", "core"), tuple(sorted({c.lower() for c in r.get("capabilities", [])})))
        seen.setdefault(key, []).append({"id": r["id"], "name": r.get("name", r.get("slug")), "kind": r["kind"], "workspace": r.get("workspace")})
    duplicates = {f"{k[0]}:{','.join(k[1])}": v for k, v in seen.items() if len(v) > 1}
    return {"duplicates": duplicates, "count": len(duplicates)}


# Drift signal types surfaced by the drift analyzers (Phase 6.2).
DRIFT_KINDS = ["architecture", "dependency", "security", "infrastructure", "documentation", "configuration"]


def detect_drifts(resource: dict, events: Iterable[dict]) -> dict:
    """Detect drift signals across all dimensions for a single resource.

    Each drift entry is a deterministic assertion derived from the resource's
    manifest state and the normalized data-lake events that touched it.
    """
    rid = resource["id"]
    security = resource.get("security", {})
    scan = security.get("scanStatus")
    health = resource.get("health", {})
    relationships = resource.get("relationships", [])
    deps = [r.get("target") for r in relationships]
    caps = {c.lower() for c in resource.get("capabilities", [])}
    obs = resource.get("observability", {})

    event_types = [e.get("type") for e in events if rid in e.get("scope", [])]

    drifts = {}

    # Architecture drift: capabilities/declared pattern diverge, or a declared
    # service capability is missing an api exposure or deployment target.
    arch = detect_architecture(resource)
    if "microservice" in arch and not resource.get("apis") and "api" not in caps:
        drifts["architecture"] = "microservice declares no exposed API or routes"
    if "api" in caps and resource.get("deployment", {}).get("status") != "active":
        drifts["architecture"] = drifts.get("architecture") or "api capability not backed by an active deployment"

    # Dependency drift: a dependency relationship points at a resource whose
    # health is degraded/critical, or a declared dependency has no relationship.
    for dep in deps:
        depres = next((d for d in resource.get("_dep_graph", []) if d["id"] == dep), None)
        if depres is not None and depres.get("health", {}).get("status") in ("degraded", "warning", "critical"):
            drifts["dependency"] = drifts.get("dependency") or f"dependency {dep} is not healthy"

    # Security drift: a findings event landed on this resource, or the scan is not
    # clean (posture has degraded since the baseline).
    if "security.findings" in event_types:
        payload = next((e.get("payload", {}) for e in events if rid in e.get("scope", []) and e.get("type") == "security.findings"), {})
        if payload.get("open_vulns", 0):
            drifts["security"] = "new security findings event recorded (open vulnerabilities)"
        else:
            drifts["security"] = drifts.get("security") or "security findings event recorded"
    if scan and scan != "clean":
        drifts["security"] = drifts.get("security") or f"security posture ({scan}) needs a clean scan"

    # Infrastructure drift: a failed deployment or unhealthy runtime state.
    if "deployment.failure" in event_types:
        drifts["infrastructure"] = "deployment failure recorded for this resource"
    if health.get("status") in ("degraded", "warning", "critical") and "deployment" in resource:
        drifts["infrastructure"] = "runtime/degradation detected in active deployment"

    # Documentation drift: lacks runbook/dashboard, has a deployment target but
    # no observability surfacing, or no summary depth.
    if resource.get("deployment") and not (obs.get("metrics") or obs.get("dashboard") or obs.get("runbook")):
        drifts["documentation"] = "no runbook, dashboard, or metrics surfaced for a deployed resource"
    if not resource.get("summary") or len(resource.get("summary", "")) < 30:
        drifts["documentation"] = drifts.get("documentation") or "summary is missing or too thin for AI/agent context"

    # Configuration drift: a real state change — a health-degrading event landed,
    # or the model declared drift on the resource's health.
    declared = health.get("drift", [])
    state_changes = {"health.degraded", "health.recovered", "deployment.failure", "security.findings"}
    if declared or (state_changes & set(event_types)):
        drifts["configuration"] = drifts.get("configuration") or "configuration changed since last baseline snapshot"

    return drifts


def analyze(resource: dict, readiness: dict, events: Iterable[dict] | None = None,
           readiness_by_id: dict | None = None) -> dict:
    """Run every analyzer for a single resource and return a normalized report."""
    resource = dict(resource)  # don't mutate input
    # Pre-resolve dependent health for dependency drift detection.
    resource["_dep_graph"] = resource.get("_dep_graph", [])
    by_id = readiness_by_id or {}
    return {
        "id": resource["id"],
        "slug": resource["slug"],
        "languages": detect_languages(resource.get("languages")),
        "frameworks": detect_frameworks(resource.get("frameworks")),
        "architecture": detect_architecture(resource),
        "api": detect_api(resource),
        "apiCompatibility": detect_api_compatibility(resource),
        "dependencies": resolve_dependencies(resource),
        "security": detect_security(resource),
        "techDebt": tech_debt(resource, readiness),
        "deprecation": detect_deprecation(resource),
        "migrationSuggestions": detect_migration_suggestions(resource, by_id),
        "costOptimization": detect_cost_optimization(resource, readiness),
        "perfRegression": detect_perf_regression(resource),
        "drift": detect_drifts(resource, events or []),
    }


def build_analyses(resources: list[dict], readiness_by_id: dict[str, dict], events: Iterable[dict] | None = None) -> dict:
    per = {}
    total_debt = 0
    deps = 0
    api_count = 0
    total_drift = 0
    drift_by_kind: dict[str, int] = {k: 0 for k in DRIFT_KINDS}
    incompat = 0
    migration_count = 0
    cost_opts = 0
    unused = 0
    # Index dependent health so dependency-drift detection can read target state.
    by_id = {r["id"]: r for r in resources}

    # Count incoming edges per resource for unused-component detection.
    incoming: dict[str, int] = {r["id"]: 0 for r in resources}
    for r in resources:
        for rel in r.get("relationships", []):
            target = rel.get("target")
            if target in incoming:
                incoming[target] = incoming.get(target, 0) + 1

    for r in resources:
        r = dict(r)
        r["_dep_graph"] = [
            {"id": rel.get("target"), "health": by_id.get(rel.get("target"), {}).get("health", {})}
            for rel in r.get("relationships", [])
        ]
        a = analyze(r, readiness_by_id[r["id"]], events, by_id)
        per[r["id"]] = a
        total_debt += 0 if a["techDebt"] == ["none detected"] else len([d for d in a["techDebt"] if d != "none detected"])
        deps += len(a["dependencies"])
        api_count += int(a["api"])
        if a["apiCompatibility"]["risk"] == "unversioned":
            incompat += 1
        migration_count += len(a["migrationSuggestions"])
        cost_opts += len(a["costOptimization"])
        if detect_unused_components(r, incoming):
            unused += 1
        for kind in DRIFT_KINDS:
            if kind in a["drift"]:
                total_drift += 1
                drift_by_kind[kind] += 1
    tech_debt_resources = sum(1 for a in per.values() if a["techDebt"] != ["none detected"])
    drift_resources = sum(1 for a in per.values() if a["drift"])
    duplicates = detect_duplicate_libraries(resources)
    return {
        "per_resource": per,
        "summary": {
            "language_count": sorted({lang for a in per.values() for lang in a["languages"]}),
            "framework_count": sorted({fw for a in per.values() for fw in a["frameworks"]}),
            "relationship_count": deps,
            "api_resources": api_count,
            "api_compatibility_risk": incompat,
            "migration_suggestions": migration_count,
            "cost_optimization_opportunities": cost_opts,
            "unused_components": unused,
            "duplicate_libraries": duplicates["count"],
            "tech_debt_resources": tech_debt_resources,
            "tech_debt_items": total_debt,
            "deprecated_resources": sum(1 for a in per.values() if a["deprecation"]["deprecated"]),
            "perf_regressions": sum(1 for a in per.values() if a["perfRegression"]["regression"]),
            "drift_resources": drift_resources,
            "drift_items": total_drift,
            "drift_by_kind": drift_by_kind,
        },
        "duplicate_libraries": duplicates["duplicates"],
    }
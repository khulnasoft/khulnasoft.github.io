"""Intelligence plane analyzers.

Analyzers run over the resource registry at build time to surface engineering
intelligence: language/framework/architecture/API/security detection, dependency
resolution, technical debt, deprecation, and performance-regression signals.
Deterministic and derived — never hand-maintained.
"""
from __future__ import annotations

# Canonical taxonomies used across analyzers.
LANGUAGES = {".ts": "typescript", ".py": "python", ".go": "go", ".rs": "rust", ".java": "java", ".cs": "c#"}
FRAMEWORKS = ["fastapi", "node", "react", "next.js", "spring", "flask", "django", "gin", "actix"]
ARCH_PATTERNS = ["microservice", "serverless", "event-driven", "layered", "monolith"]


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
    return {"regression": bool(degraded), "signal": obs.get("p99_label") or ("health {status}".format(status=health.get("status")) if degraded else None)}


def analyze(resource: dict, readiness: dict) -> dict:
    """Run every analyzer for a single resource and return a normalized report."""
    return {
        "id": resource["id"],
        "slug": resource["slug"],
        "languages": detect_languages(resource.get("languages")),
        "frameworks": detect_frameworks(resource.get("frameworks")),
        "architecture": detect_architecture(resource),
        "api": detect_api(resource),
        "dependencies": resolve_dependencies(resource),
        "security": detect_security(resource),
        "techDebt": tech_debt(resource, readiness),
        "deprecation": detect_deprecation(resource),
        "perfRegression": detect_perf_regression(resource),
    }


def build_analyses(resources: list[dict], readiness_by_id: dict[str, dict]) -> dict:
    per = {}
    total_debt = 0
    deps = 0
    api_count = 0
    for r in resources:
        a = analyze(r, readiness_by_id[r["id"]])
        per[r["id"]] = a
        total_debt += 0 if a["techDebt"] == ["none detected"] else len([d for d in a["techDebt"] if d != "none detected"])
        deps += len(a["dependencies"])
        api_count += int(a["api"])
    tech_debt_resources = sum(1 for a in per.values() if a["techDebt"] != ["none detected"])
    return {
        "per_resource": per,
        "summary": {
            "language_count": sorted({lang for a in per.values() for lang in a["languages"]}),
            "framework_count": sorted({fw for a in per.values() for fw in a["frameworks"]}),
            "relationship_count": deps,
            "api_resources": api_count,
            "tech_debt_resources": tech_debt_resources,
            "tech_debt_items": total_debt,
            "deprecated_resources": sum(1 for a in per.values() if a["deprecation"]["deprecated"]),
            "perf_regressions": sum(1 for a in per.values() if a["perfRegression"]["regression"]),
        },
    }
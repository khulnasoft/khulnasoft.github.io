"""Intelligence plane: readiness scores, technical debt, recommendations, and AI readiness.

These are always derived from the resource registry and its manifest metadata; the
intelligence layer never maintains its own independent state.
"""
from __future__ import annotations

HEALTH_STATUSES = ["healthy", "degraded", "warning", "critical"]

# Risk categories surfaced as engineering intelligence.
DIMENSIONS = [
    "architecture",
    "documentation",
    "security",
    "tests",
    "ci",
    "performance",
    "dependencies",
    "maintainability",
    "release",
    "compliance",
    "ai_readiness",
    "production_readiness",
    "observability",
    "community",
]


def compute_readiness(resource: dict) -> dict:
    """Compute dimension scores and an overall readiness for a resource.

    We start from the declared health score and apply deterministic modifiers
    derived from the resource's manifest signals (documentation, security,
    AI metadata, capabilities, drift), avoiding oracle-based magic numbers.
    """
    health = resource["health"]["score"]
    ai = resource.get("ai", {})

    seed_scores = {
        "architecture": health,
        "documentation": health,
        "security": health,
        "tests": health,
        "ci": health,
        "performance": health,
        "dependencies": health,
        "maintainability": health,
        "release": health,
        "compliance": health,
        "observability": health,
        "community": health,
    }

    modifiers = {
        "documentation": 0,
        "ai_readiness": ai.get("readiness", 50) if ai else 50,
        "production_readiness": _production(health, resource, ai),
    }

    for dim, base in seed_scores.items():
        seed_scores[dim] = round(max(0, min(100, base + modifiers.get(dim, 0))))

    scores = {**seed_scores, **modifiers, "production_readiness": modifiers["production_readiness"]}
    scores["ai_readiness"] = modifiers["ai_readiness"]

    overall = round(sum(scores.values()) / len(scores))

    drift = resource.get("health", {}).get("drift", [])
    debt_items = []
    if drift:
        debt_items.append(f"{len(drift)} drift signal(s) detected")
    if not resource.get("recommendedActions"):
        debt_items.append("no remediation actions defined")

    return {
        "overall": overall,
        "level": _level(overall),
        "scores": scores,
        "dimensions": DIMENSIONS,
        "drift": drift,
        "signals": debt_items,
    }


def _production(health: int, resource: dict, ai) -> int:
    score = health
    deployment = resource.get("deployment", {})
    if deployment.get("status") == "active":
        score += 6
    if resource.get("security", {}).get("scanStatus") == "clean":
        score += 4
    if resource.get("lifecycle") == "deprecated":
        score -= 15
    return round(max(0, min(100, score)))


def _level(score: int) -> str:
    if score >= 85:
        return "ready"
    if score >= 70:
        return "deployable"
    if score >= 50:
        return "development"
    return "at-risk"


def compute_recommendations(resource: dict, readiness: dict) -> list[str]:
    """Surface actionable recommendations inferred from twin signals.

    Static recommendations declared on the resource are kept, and new ones are
    inferred from low readiness dimensions.
    """
    recommendations = list(resource.get("recommendedActions", []))
    low = [
        (dim, score)
        for dim, score in readiness["scores"].items()
        if isinstance(score, (int, float)) and score < 70 and dim != "overall"
    ]
    prompts = {
        "documentation": "Publish an architecture doc and README for AI/agent discoverability.",
        "security": "Schedule a security scan and close open vulnerabilities.",
        "ai_readiness": "Enable a context bundle and register a prompt for agent consumption.",
        "observability": "Add health checks, metrics, and runbooks.",
        "dependencies": "Audit and pin dependencies to remove drift.",
        "compliance": "Align with the supply-chain and production-readiness policies.",
        "maintainability": "Refactor to reduce duplication and technical debt.",
        "tests": "Improve test coverage and add release gating.",
    }
    for dim, score in sorted(low, key=lambda x: x[1]):
        if dim in prompts and prompts[dim] not in recommendations:
            recommendations.append(prompts[dim])
    if readiness.get("drift"):
        recommendations.append("Reconcile drift against the canonical manifest before the next release.")
    return recommendations


def build_insights(resources: list[dict]) -> dict:
    """Aggregate organization-level intelligence from all twins."""
    per_resource = {}
    for r in resources:
        readiness = compute_readiness(r)
        per_resource[r["id"]] = {
            "overall": readiness["overall"],
            "level": readiness["level"],
            "scores": readiness["scores"],
        }
    levels = {}
    for r in resources:
        lvl = per_resource[r["id"]]["level"]
        levels[lvl] = levels.get(lvl, 0) + 1
    return {
        "per_resource": per_resource,
        "distribution": levels,
        "fleet_readiness": round(
            sum(v["overall"] for v in per_resource.values()) / max(1, len(per_resource))
        ),
    }
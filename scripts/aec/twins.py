"""Engineering digital twin derivation.

A digital twin is the canonical, continuously updated representation of a
resource. Twins are *computed* from the resource definition + derived layers
(readiness, capabilities, context) so every downstream artifact (graph, portal,
recommendations) shares one source of truth.
"""
from __future__ import annotations


def build_twin(resource: dict, readiness: dict, recommendations: list[str], context_summary: str) -> dict:
    """Compose the canonical digital twin for a single resource."""
    ai = resource.get("ai", {})
    return {
        "resource": {
            "id": resource["id"],
            "kind": resource["kind"],
            "name": resource["name"],
            "slug": resource["slug"],
            "owner": resource.get("owner"),
            "team": resource.get("team"),
            "workspace": resource.get("workspace"),
            "lifecycle": resource.get("lifecycle"),
            "status": resource.get("status"),
            "visibility": resource.get("visibility"),
            "version": resource.get("version"),
            "summary": resource["summary"],
            "source": resource.get("source", "generated"),
            "updatedAt": resource.get("updatedAt"),
        },
        "source_state": {
            "languages": resource.get("languages", []),
            "frameworks": resource.get("frameworks", []),
            "capabilities": resource.get("capabilities", []),
            "security": resource.get("security", {}),
            "deployment": resource.get("deployment", {}),
        },
        "relationships": resource.get("relationships", []),
        "health": resource.get("health", {}),
        "readiness": readiness,
        "intelligence": {
            "drift": resource.get("health", {}).get("drift", []),
            "signals": readiness.get("signals", []),
        },
        "ai": {
            "contextBundle": ai.get("contextBundle", False),
            "promptRegistry": ai.get("promptRegistry", False),
            "agentReady": ai.get("agentReady", False),
            "readiness": ai.get("readiness"),
        },
        "context_summary": context_summary,
        "recommended_actions": recommendations,
    }


def build_all_twins(resources: list[dict], insights: dict, ready_by_id: dict, context_by_id: dict) -> dict:
    """Build twins for every resource; ready_by_id and context_by_id are keyed by resource id."""
    twins = {}
    for r in resources:
        readiness = insights["per_resource"].get(r["id"], {})
        recommendations = ready_by_id.get(r["id"], [])
        context_summary = context_by_id.get(r["id"], {}).get("summary", "")
        twins[r["id"]] = build_twin(r, readiness, recommendations, context_summary)
    return twins
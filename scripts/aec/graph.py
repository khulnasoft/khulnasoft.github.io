"""Knowledge graph derivation and metrics."""
from __future__ import annotations


def build_graph(resources: list[dict]) -> dict:
    """Derive the knowledge graph from resource relationships.

    Nodes are derived from the registry and edges exclusively from the
    `relationships` declared on each resource, so the graph is never a
    hand-maintained artifact.
    """
    nodes = [
        {
            "id": r["id"],
            "label": r["name"],
            "slug": r["slug"],
            "kind": r["kind"],
            "workspace": r.get("workspace", "core"),
            "health": r["health"]["status"],
        }
        for r in resources
    ]

    edges = []
    for r in resources:
        for rel in r.get("relationships", []):
            edges.append(
                {
                    "from": r["id"],
                    "to": rel["target"],
                    "type": rel.get("type", "related"),
                    "detail": rel.get("detail", ""),
                }
            )

    metrics = _compute_metrics(resources)

    return {"nodes": nodes, "edges": edges, "metrics": metrics}


def _compute_metrics(resources: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for r in resources:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1

    health_scores = [r["health"]["score"] for r in resources] or [0]
    healthy = sum(1 for r in resources if r["health"]["status"] == "healthy")
    health_score = round(sum(health_scores) / len(health_scores))
    reliability_score = min(100, health_score + 5)

    automation = sum(1 for r in resources if r["kind"] in {
        "workflow", "pipeline", "job", "function", "worker", "cronjob"
    })
    automation_coverage = round(automation / len(resources) * 100) if resources else 0

    context = sum(1 for r in resources if r.get("ai", {}).get("contextBundle"))
    context_coverage = round(context / len(resources) * 100) if resources else 0

    return {
        "resource_count": len(resources),
        "kind_distribution": counts,
        "health_score": health_score,
        "reliability_score": round(sum(
            r["health"]["score"] for r in resources if r["health"]["status"] == "healthy"
        ) / max(1, sum(1 for r in resources if r["health"]["status"] == "healthy"))),
        "automation_coverage": automation_coverage,
        "context_coverage": context_coverage,
    }
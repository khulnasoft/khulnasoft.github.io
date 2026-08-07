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


def _adjacency(resources: list[dict]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Build forward (depends_on) and reverse (dependents) adjacency sets."""
    forward: dict[str, set[str]] = {r["id"]: set() for r in resources}
    reverse: dict[str, set[str]] = {r["id"]: set() for r in resources}
    for r in resources:
        for rel in r.get("relationships", []):
            target = rel["target"]
            forward[r["id"]].add(target)
            reverse.setdefault(target, set()).add(r["id"])
    return forward, reverse


def reachable(start: str, adjacency: dict[str, set[str]]) -> set[str]:
    """Return all nodes reachable from `start` via the given adjacency (BFS)."""
    seen: set[str] = set()
    stack = [start]
    while stack:
        cur = stack.pop()
        for nxt in adjacency.get(cur, set()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    seen.discard(start)
    return seen


def compute_impact(resources: list[dict]) -> dict:
    """Derive per-resource change-impact: downstream blast radius, ranked.

    Edge direction: `A depends_on B` means a change to B can impact A. So the
    affected set for resource X is everything reachable by following the
    reverse (dependents) edges from X.
    """
    node_ids = [r["id"] for r in resources]
    forward, reverse = _adjacency(resources)
    names = {r["id"]: r["name"] for r in resources}
    kinds = {r["id"]: r["kind"] for r in resources}

    per_resource = {}
    for rid in node_ids:
        affected = reachable(rid, reverse)
        ranked = sorted(
            affected,
            key=lambda n: (len(reverse.get(n, set())), names.get(n, n)),
            reverse=True,
        )
        per_resource[rid] = {
            "id": rid,
            "name": names.get(rid, rid),
            "kind": kinds.get(rid, "?"),
            "blast_radius": len(affected),
            "impacted": [
                {"id": n, "name": names.get(n, n), "kind": kinds.get(n, "?"), "depth": _depth(rid, n, reverse)}
                for n in ranked
            ],
            "is_dependency": bool(forward.get(rid, set())),
        }
    losses = [v["blast_radius"] for v in per_resource.values()]
    edges = []
    for r in resources:
        for rel in r.get("relationships", []):
            edges.append({"from": r["id"], "to": rel["target"], "type": rel.get("type", "related")})
    return {
        "nodes": [
            {"id": r["id"], "name": r["name"], "kind": r["kind"], "slug": r["slug"]} for r in resources
        ],
        "edges": edges,
        "per_resource": per_resource,
        "total": len(resources),
        "max_blast_radius": max(losses) if losses else 0,
        "avg_blast_radius": round(sum(losses) / len(losses)) if losses else 0,
    }


def _depth(target: str, start: str, reverse: dict[str, set[str]]) -> int:
    """Shortest number of hops from the starting resource to `target` downstream."""
    if target == start:
        return 0
    depth = 0
    frontier = {start}
    seen = {start}
    while frontier:
        depth += 1
        nxt: set[str] = set()
        for cur in frontier:
            for m in reverse.get(cur, set()):
                if m == target:
                    return depth
                if m not in seen:
                    seen.add(m)
                    nxt.add(m)
        frontier = nxt
    return -1


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
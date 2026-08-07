"""Knowledge plane and context fabric.

The AI-ready context fabric composes layered, agent-consumable context for a
resource and publishes composable AI outputs (llms.txt, llms-full.txt, MCP
metadata). Context supports selective retrieval: consumers request only the
layers they need instead of always pulling a monolithic bundle.
"""
from __future__ import annotations

from typing import Iterable

LAYERS = [
    "metadata",
    "architecture",
    "dependency",
    "api",
    "workflow",
    "deployment",
    "runtime",
    "observability",
    "security",
    "business",
]


def compose_layer(layer: str, resource: dict) -> dict | None:
    """Return the context payload for a single layer, or None if not applicable."""
    if layer == "metadata":
        return {
            "summary": resource["summary"],
            "name": resource["name"],
            "kind": resource["kind"],
            "owner": resource.get("owner"),
            "team": resource.get("team"),
            "workspace": resource.get("workspace"),
            "lifecycle": resource.get("lifecycle"),
            "status": resource.get("status"),
            "visibility": resource.get("visibility"),
            "version": resource.get("version"),
            "tags": resource.get("tags", []),
            "labels": resource.get("labels", {}),
        }
    if layer == "architecture":
        return {
            "languages": resource.get("languages", []),
            "frameworks": resource.get("frameworks", []),
            "capabilities": resource.get("capabilities", []),
        }
    if layer == "dependency":
        return {
            "relationships": [
                {"type": rel.get("type"), "target": rel.get("target"), "detail": rel.get("detail")}
                for rel in resource.get("relationships", [])
            ]
        }
    if layer == "api":
        return {"apis": resource.get("apis", []), "exposes": resource.get("exposes", [])}
    if layer == "workflow":
        return {"workflows": resource.get("workflows", []), "ci": resource.get("ci", {})}
    if layer == "deployment":
        return {
            "deployment": resource.get("deployment", {}),
            "targets": resource.get("deployment", {}).get("targets", []),
        }
    if layer == "runtime":
        return {
            "runtime": {
                "status": resource.get("deployment", {}).get("status", resource.get("status")),
                "environment": resource.get("deployment", {}).get("environment"),
            }
        }
    if layer == "observability":
        return resource.get("observability", {})
    if layer == "security":
        return resource.get("security", {})
    if layer == "business":
        return {"summary": resource["summary"], "owner": resource.get("owner"), "workspace": resource.get("workspace")}
    return None


def compose_context(resource: dict, readiness: dict, layers: Iterable[str] | None = None) -> dict:
    """Compose the layered context bundle for a resource.

    If `layers` is provided, only those layers are composed (selective
    retrieval). A `health` layer is always appended.
    """
    layer_names = list(layers) if layers else LAYERS
    context = {}
    for layer in LAYERS:
        if layer in layer_names:
            payload = compose_layer(layer, resource)
            if payload:
                context[layer] = payload
    context["health"] = {
        "score": resource["health"]["score"],
        "status": resource["health"]["status"],
        "readiness": readiness.get("overall"),
    }
    return context


def build_context(resource: dict, readiness: dict) -> dict:
    """Full context bundle for an API/agent consumer."""
    return {
        "resource": {"id": resource["id"], "name": resource["name"], "slug": resource["slug"], "kind": resource["kind"]},
        "context": compose_context(resource, readiness),
        "summary": resource["summary"],
        "layers": LAYERS,
    }


def build_llms(resources: list[dict]) -> str:
    """Generate llms.txt: a concise AI-consumable index of the ecosystem."""
    out = [
        "# KhulnaSoft Engineering Knowledge OS",
        "",
        "> Developer portal, AI context platform, and control plane: a living engineering knowledge OS for the ecosystem.",
        "> Continuously updated control plane for engineering assets, AI-ready context, and agent-friendly APIs.",
        "",
        "## Resources",
        "",
    ]
    for r in resources:
        out.append(f"- [{r['name']}](https://khulnasoft.github.io/resources/{r['slug']}.html)")
        out.append(f"  - Context: `/context/{r['slug']}.json`")
        out.append(f"  - Twin: `/api/resources/{r['slug']}/twin`")
    return "\n".join(out) + "\n"


def build_llms_full(resources: list[dict]) -> str:
    """Generate llms-full.txt: fully inlined AI-ready knowledge."""
    out = ["# KhulnaSoft Engineering Knowledge OS (full)", ""]
    for r in resources:
        out.append(f"## {r['name']} ({r['kind']})")
        out.append(f"- Summary: {r['summary']}")
        out.append(f"- Owner: {r.get('owner')} | Workspace: {r.get('workspace')} | Lifecycle: {r.get('lifecycle')}")
        if r.get("capabilities"):
            out.append(f"- Capabilities: {', '.join(r['capabilities'])}")
        if r.get("relationships"):
            rels = "; ".join(f"{x['type']} {x['target']}" for x in r["relationships"])
            out.append(f"- Relationships: {rels}")
        out.append(f"- Health: {r['health']['score']}/100 ({r['health']['status']})")
        out.append(f"- Rendering: {r.get('updatedAt')}")
        out.append("")
    return "\n".join(out) + "\n"


def build_mcp_metadata(resources: list[dict]) -> dict:
    """MCP metadata exposed by the runtime plane (Model Context Protocol)."""
    return {
        "protocol": "model-context-protocol",
        "server": "khulnasoft-aec",
        "resources": [
            {
                "id": r["id"],
                "name": r["name"],
                "slug": r["slug"],
                "kind": r["kind"],
                "endpoint": f"mcp://khulnasoft/context/{r['slug']}",
                "layers": LAYERS,
            }
            for r in resources
        ],
        "layers": LAYERS,
        "selective": True,
    }
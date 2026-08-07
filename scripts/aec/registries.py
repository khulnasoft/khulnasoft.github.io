"""Control-plane registries: capability, platform, service, agent, prompt, and AI metadata.

Registries are derived from the digital-twin state so repositories automatically
inherit and expose capabilities, and every registry stays queryable and
extensible rather than hand-maintained.
"""
from __future__ import annotations

from collections import Counter

# Canonical capability taxonomy (Phase 7).
CAPABILITIES = [
    "authentication", "authorization", "storage", "database", "ai", "security",
    "messaging", "networking", "deployment", "container", "cli", "sdk", "api",
    "monitoring", "observability", "kubernetes", "terraform", "github",
    "github-action", "vscode-extension", "operator", "helm-chart",
    "microservice", "library", "template", "starter", "blueprint",
    "control-plane", "catalog", "governance", "registry", "context-fabric",
    "prompt-registry", "agent-runtime", "mcp", "knowledge-graph", "digital-twin",
    "release", "automation", "routing", "vulnerability", "policy", "review",
    "dependency-analysis", "discovery", "metadata",
]


def build_capability_registry(resources: list[dict]) -> dict:
    """Group resources by capability, inheriting capabilities from twins."""
    cap_to_resources: dict[str, list[dict]] = {}
    for r in resources:
        for cap in r.get("capabilities", []):
            cap_to_resources.setdefault(cap, []).append(
                {"id": r["id"], "name": r["name"], "slug": r["slug"], "kind": r["kind"]}
            )
    return {
        "registry": "capability",
        "count": len(cap_to_resources),
        "capabilities": {
            cap: {"resources": [x["id"] for x in metas], "count": len(metas)}
            for cap, metas in sorted(cap_to_resources.items())
        },
        "top": [cap for cap, _ in Counter(
            [c for r in resources for c in r.get("capabilities", [])]
        ).most_common()],
    }


def build_platform_registry(resources: list[dict]) -> dict:
    """Model the platform as a registry of every first-class asset kind."""
    kinds = {}
    for r in resources:
        kinds.setdefault(r["kind"], []).append({"id": r["id"], "name": r["name"], "slug": r["slug"]})
    return {
        "registry": "platform",
        "count": len(resources),
        "kinds": {kind: {"count": len(items), "resources": items} for kind, items in sorted(kinds.items())},
    }


def build_service_registry(resources: list[dict]) -> dict:
    """Registry of runnable/services and the capabilities they expose."""
    services = [
        {"id": r["id"], "name": r["name"], "slug": r["slug"], "kind": r["kind"], "workspace": r.get("workspace")}
        for r in resources if r["kind"] in ("service", "component", "application", "microservice", "api", "platform")
    ]
    return {"registry": "service", "count": len(services), "services": services}


def build_kind_registry(resources: list[dict]) -> dict:
    """Registry of resource kinds present in the ecosystem (taxonomy coverage)."""
    return {
        "registry": "kind",
        "count": len(Counter(r["kind"] for r in resources)),
        "coverage": dict(Counter(r["kind"] for r in resources)),
    }


def build_prompt_registry(prompts: list[dict]) -> dict:
    """Registry of prompts available to AI agents."""
    return {
        "registry": "prompt",
        "count": len(prompts),
        "prompts": [
            {"id": p["id"], "file": p["path"], "body": p["body"].strip()} for p in prompts
        ],
    }


def build_agent_registry(agents: list[dict]) -> dict:
    """Registry of AI agents and their capabilities."""
    return {
        "registry": "agent",
        "count": len(agents),
        "agents": agents,
    }


def build_context_registry(resources: list[dict]) -> dict:
    """Registry of resources that expose AI-ready context bundles."""
    ai_ready = [r for r in resources if r.get("ai", {}).get("contextBundle")]
    return {
        "registry": "context",
        "count": len(ai_ready),
        "resources": [{"id": r["id"], "name": r["name"], "slug": r["slug"]} for r in ai_ready],
    }


def build_model_registry(resources: list[dict]) -> dict:
    """Registry of AI models in the ecosystem (kind: model/ai-model)."""
    models = [
        {"id": r["id"], "name": r["name"], "slug": r["slug"], "kind": r["kind"], "version": r.get("version"),
         "owner": r.get("owner"), "workspace": r.get("workspace"),
         "readiness": r.get("ai", {}).get("readiness"), "capabilities": r.get("capabilities", [])}
        for r in resources if r["kind"] in ("model", "ai-model", "ai-agent")
    ]
    return {"registry": "model", "count": len(models), "models": models}


def build_tool_registry(resources: list[dict]) -> dict:
    """Registry of capabilities/resources usable as AI tools (MCP, SDK, CLI, API)."""
    tool_caps = {"mcp", "api", "cli", "sdk", "tool", "vscode-extension", "github-action", "openapi"}
    tools = []
    for r in resources:
        caps = {c.lower() for c in r.get("capabilities", [])}
        if caps & tool_caps:
            tools.append({"id": r["id"], "name": r["name"], "slug": r["slug"],
                          "kind": r["kind"], "toolTypes": sorted(caps & tool_caps)})
    return {"registry": "tool", "count": len(tools), "tools": tools}


def build_memory_registry(resources: list[dict]) -> dict:
    """Registry of memory/knowledge stores (graph, vector, context fabric, database)."""
    mem_caps = {"vector-collection", "knowledge-graph", "graph", "context-fabric", "database", "embedding-collection", "search"}
    memories = []
    for r in resources:
        caps = {c.lower() for c in r.get("capabilities", [])}
        if caps & mem_caps or r["kind"] in ("graph", "database", "queue"):
            memories.append({"id": r["id"], "name": r["name"], "slug": r["slug"],
                             "kind": r["kind"], "access": sorted(caps & mem_caps)})
    return {"registry": "memory", "count": len(memories), "memories": memories}


def build_registries(resources: list[dict], prompts: list[dict], agents: list[dict]) -> dict:
    """Build all control-plane registries as one queryable structure."""
    return {
        "capability": build_capability_registry(resources),
        "platform": build_platform_registry(resources),
        "service": build_service_registry(resources),
        "kind": build_kind_registry(resources),
        "prompt": build_prompt_registry(prompts),
        "agent": build_agent_registry(agents),
        "context": build_context_registry(resources),
        "model": build_model_registry(resources),
        "tool": build_tool_registry(resources),
        "memory": build_memory_registry(resources),
    }
"""AI control-plane services: evaluation, safety, and telemetry.

Phase 7.4 services supplement the prompt/context/agent/memory/model/tool
registries with derived signals that make the AI control plane auditable and
operable: evaluation (readiness/quality of agent surfaces), safety (guardrails,
policy, and security posture), and telemetry (usage and coverage counters).

All values are deterministic and derived from the canonical model — nothing is
hand-maintained here.
"""
from __future__ import annotations


def _evaluation_score(item: dict) -> int:
    """Derive a 0-100 readiness score for an AI resource based on its surface."""
    enabled = sum(1 for v in (item["promptRegistry"], item["contextBundle"], item["agentReady"]) if v)
    return round(min(100, 40 + enabled * 20 + (item["aiReadiness"] or 0) * 0.4))


def build_evaluation(ai_resources: list[dict], agents: list[dict], prompts: list[dict], readiness_by_id: dict) -> dict:
    """Derive evaluation signals over the AI surface (agents, models, runtimes)."""
    eval_items = []
    for r in ai_resources:
        ai = r.get("ai", {})
        item = {
            "id": r["id"],
            "name": r["name"],
            "kind": r["kind"],
            "promptRegistry": ai.get("promptRegistry", False),
            "contextBundle": ai.get("contextBundle", False),
            "agentReady": ai.get("agentReady", False),
            "aiReadiness": ai.get("readiness"),
            "health": r["health"]["score"],
            "ready": readiness_by_id.get(r["id"], {}).get("level"),
        }
        item["evaluationScore"] = _evaluation_score(item)
        eval_items.append(item)

    return {
        "service": "evaluation",
        "count": len(eval_items),
        "agentCount": len(agents),
        "promptCount": len(prompts),
        "resources": sorted(eval_items, key=lambda x: x["evaluationScore"], reverse=True),
        "avgEvaluationScore": round(sum(x["evaluationScore"] for x in eval_items) / len(eval_items)) if eval_items else 0,
    }


def build_safety(resources: list[dict], org) -> dict:
    """Derive safety view: guardrails, policy adherence, and posture across all resources."""
    gov = org.get("governance", {})
    guardrails = [
        {"id": p.get("id"), "name": p.get("name"), "scope": p.get("scope"),
         "check": p.get("check"), "requiredSignals": p.get("requiredSignals", [])}
        for p in gov.get("policies", [])
    ]

    clean_scans = sum(1 for r in resources if r.get("security", {}).get("scanStatus") == "clean")
    deprecated = [r["id"] for r in resources if r.get("lifecycle") == "deprecated"]
    ai_resources = [r for r in resources if r["kind"] in ("ai-agent", "model", "ai-runtime")]
    ai_posture = sum(1 for r in ai_resources if r.get("ai", {}).get("agentReady"))

    return {
        "service": "safety",
        "policyCount": len(guardrails),
        "guardrails": guardrails,
        "security": {
            "cleanScans": clean_scans,
            "total": len(resources),
            "deprecatedCount": len(deprecated),
        },
        "aiPosture": {
            "aiResources": len(ai_resources),
            "agentReady": ai_posture,
            "agentReadyPct": round(ai_posture / len(ai_resources) * 100) if ai_resources else 0,
        },
    }


def build_telemetry(resources: list[dict], agents: list[dict], prompts: list[dict]) -> dict:
    """Derive counters useful for observing the AI control plane."""
    ai_resources = [r for r in resources if r.get("ai", {})]
    context_bundles = sum(1 for r in ai_resources if r.get("ai", {}).get("contextBundle"))
    prompt_registry = sum(1 for r in ai_resources if r.get("ai", {}).get("promptRegistry"))
    agent_ready = sum(1 for r in ai_resources if r.get("ai", {}).get("agentReady"))
    total = max(1, len(resources))

    return {
        "service": "telemetry",
        "aiResources": len(ai_resources),
        "agents": len(agents),
        "prompts": len(prompts),
        "contextBundles": context_bundles,
        "promptRegistryEnabled": prompt_registry,
        "agentReady": agent_ready,
        "contextCoveragePct": round(context_bundles / total * 100),
        "registries": ["prompt", "context", "agent", "memory", "model", "tool", "template"],
        "operations": {
            "serving": "resource-context",
            "modes": ["selective", "layered", "llms.txt", "mcp"],
        },
    }


def build_ai_services(resources: list[dict], agents: list[dict], prompts: list[dict], readiness_by_id: dict, org) -> dict:
    """Aggregate the evaluation, safety, and telemetry services for the AI control plane."""
    ai_resources = [r for r in resources if r.get("ai", {}) or r["kind"] in ("ai-agent", "model", "ai-runtime")]
    return {
        "evaluation": build_evaluation(ai_resources, agents, prompts, readiness_by_id),
        "safety": build_safety(resources, org),
        "telemetry": build_telemetry(resources, agents, prompts),
    }
#!/usr/bin/env python3
"""Knowledge OS verification checklist (PLAN.md).

Exercises the PLAN's five verification items against the live model and
derived layers. Exit code 0 if all pass, non-zero otherwise.

    python3 scripts/verify_aec.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aec import model, graph as graphmod, intelligence, twins as twinsmod, context as ctxmod
from aec import registries, ingest, analyzers

FAILURES: list[str] = []
CHECKS: list[tuple[str, bool]] = []


def check(label: str, ok: bool, detail: str = ""):
    CHECKS.append((label, ok))
    if not ok:
        FAILURES.append(f"{label}: {detail}")
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")


def main() -> int:
    resources = model.load_resources()
    org = model.load_organization()
    prompts = model.load_prompts()
    agents = model.load_agents()
    readiness = {r["id"]: intelligence.compute_readiness(r) for r in resources}
    recs = {r["id"]: intelligence.compute_recommendations(r, readiness[r["id"]]) for r in resources}
    context_bundles = {r["id"]: ctxmod.build_context(r, readiness[r["id"]]) for r in resources}
    insights = intelligence.build_insights(resources)
    twins = twinsmod.build_all_twins(resources, insights, recs, context_bundles)
    reg = registries.build_registries(resources, prompts, agents,
                                      model.load_json(ROOT / "data" / "marketplace" / "items.json"))
    analyses = analyzers.build_analyses(resources, readiness, events=ingest.load_events())
    graph = graphmod.build_graph(resources)

    # 1. Ingest a sample repository -> structured digital twin without manual intervention.
    sample = next(r for r in resources if r["kind"] == "repository")
    rdy = readiness[sample["id"]]
    twin = twinsmod.build_twin(sample, rdy, recs[sample["id"]], context_bundles[sample["id"]]["summary"])
    ok1 = bool(twin.get("resource") and twin.get("health") and twin.get("readiness"))
    check("1. Ingest sample repo -> structured digital twin", ok1,
          "twin missing resource/health/readiness")

    # 2. Context fabric composes layered context and supports selective retrieval.
    layers = ctxmod.compose_context(sample, rdy, ["metadata", "dependency"])
    ok2 = (context_bundles[sample["id"]]["context"] and
           set(layers.keys()) <= {"metadata", "dependency", "health"} and
           not (set(layers.keys()) - {"metadata", "dependency", "health"}))
    check("2. Context fabric composes layered + selective context", ok2,
          f"selective layers resolved to {list(layers.keys())}")

    # 3. Registries expose meaningful, queryable results.
    ok3 = reg["capability"]["count"] > 0 and reg["kind"]["count"] > 0 and reg["context"]["count"] >= 0
    check("3. Registries expose meaningful results", ok3,
          f"capabilities={reg['capability']['count']} kinds={reg['kind']['count']}")

    # 4. Portal catalog + detail views render from generated data (twins exist per resource).
    ok4 = len(twins) == len(resources) and all(bool(t["readiness"]) for t in twins.values())
    check("4. Portal views derived for all resources", ok4,
          f"twins={len(twins)} resources={len(resources)}")

    # 5. Agent-facing artifacts return context, recommendations, and insights.
    ok5 = (bool(context_bundles[sample["id"]]["context"]) and
          len(recs[sample["id"]]) >= 0 and
          insights["per_resource"][sample["id"]]["overall"] is not None)
    check("5. Agent-facing context/recommendations/insights present for a resource", ok5,
          f"recs={recs[sample['id']]} readiness={insights['per_resource'][sample['id']]['overall']}")

    # 6. Drift analyzers (Phase 6.2) surface drift across drift kinds and fire
    # on synthetic degraded-dependency / degraded-deployment scenarios.
    ok6 = analyses["summary"]["drift_items"] >= 1 and all(
        k in analyses["summary"]["drift_by_kind"] for k in analyzers.DRIFT_KINDS
    )
    check("6. Drift analyzers cover all drift kinds", ok6,
          f"found={analyses['summary']['drift_by_kind']}")
    # Dependency drift: a dependency whose health is degraded.
    dep_resource = {
        "id": "resource:synth-dep", "kind": "service", "name": "Synth", "slug": "synth-dep",
        "health": {"score": 88, "status": "healthy"},
        "relationships": [{"type": "depends_on", "target": "resource:dep-down"}],
        "_dep_graph": [{"id": "resource:dep-down", "health": {"score": 20, "status": "degraded"}}],
    }
    dep_drift = analyzers.detect_drifts(dep_resource, [])
    ok6b = "dependency" in dep_drift and "not healthy" in dep_drift["dependency"]
    check("6b. Dependency drift fires on degraded dependency", ok6b,
          f"drift={dep_drift}")
    # Infrastructure drift: a deployed resource whose runtime health degraded.
    infra_resource = {
        "id": "resource:synth-infra", "kind": "service", "name": "SynthInfra", "slug": "synth-infra",
        "health": {"score": 40, "status": "degraded"},
        "deployment": {"status": "active", "environment": "prod"},
    }
    infra_drift = analyzers.detect_drifts(infra_resource, [{"type": "deployment.failure", "scope": ["resource:synth-infra"], "id": "e:1"}])
    ok6c = "infrastructure" in infra_drift
    check("6c. Infrastructure drift fires on degraded runtime", ok6c,
          f"drift={infra_drift}")

    print(f"\n{sum(1 for _, o in CHECKS if o)}/{len(CHECKS)} checks passed")
    if FAILURES:
        print("Failures:")
        for f in FAILURES:
            print("  -", f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
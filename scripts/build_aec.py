#!/usr/bin/env python3
"""KhulnaSoft AI-Native Engineering Cloud build.

Loads the canonical model, derives the knowledge graph, intelligence, digital
twins, context fabric, and control-plane registries, then renders the static
portal and publishes machine-readable artifacts (JSON, llms.txt, etc.).

    python3 scripts/build_aec.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from aec import model, graph as graphmod, intelligence, twins as twinsmod, context as ctxmod, registries, history as hist, governance, ingest, analyzers, runtime as rtmod, sdks
from aec import render

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
KEEP = {"README.md"}


def clean_site():
    if SITE.exists():
        for child in SITE.iterdir():
            if child.name in KEEP:
                continue
            if child.is_dir():
                import shutil
                shutil.rmtree(child)
            else:
                child.unlink()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "context").mkdir(parents=True, exist_ok=True)
    (SITE / "twins").mkdir(parents=True, exist_ok=True)
    (SITE / "resources").mkdir(parents=True, exist_ok=True)
    (SITE / "docs").mkdir(parents=True, exist_ok=True)


def write(path: Path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, (dict, list)):
        content = json.dumps(content, indent=2, ensure_ascii=False)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    data = model.load_all()
    events = ingest.load_events()
    resources, applied = ingest.apply_events(model.load_resources(), events)
    org = data["organization"]
    event_summary = ingest.summarize(events, resources)

    prior_history = hist.load_state(SITE / "history.json")

    clean_site()

    graph = graphmod.build_graph(resources)
    impact = graphmod.compute_impact(resources)
    insights = intelligence.build_insights(resources)

    readiness_by_id = {r["id"]: intelligence.compute_readiness(r) for r in resources}
    recs_by_id = {
        r["id"]: intelligence.compute_recommendations(r, readiness_by_id[r["id"]])
        for r in resources
    }
    analyses = analyzers.build_analyses(resources, readiness_by_id)
    ctx_by_id = {r["id"]: ctxmod.build_context(r, readiness_by_id[r["id"]]) for r in resources}
    twins_all = twinsmod.build_all_twins(resources, insights, recs_by_id, ctx_by_id)
    reg = registries.build_registries(resources, data["prompts"], data["agents"])
    release = governance.evaluate_release(resources, readiness_by_id, org)
    runtime_state = rtmod.build_runtime(events, rtmod.load_automations())
    sdk_artifacts = sdks.generate_sdks()
    marketplace = model.load_json(ROOT / "data" / "marketplace" / "items.json")
    metrics = graphmod._compute_metrics(resources)
    metrics["events"] = event_summary

    # ---- derived artifacts ----
    write(SITE / "graph-data.json", {"nodes": graph["nodes"], "edges": graph["edges"]})
    write(SITE / "impact.json", impact)
    write(SITE / "analytics.json", analyses)
    write(SITE / "release.json", release)
    write(SITE / "manifests.json", [{"path": m["path"]} for m in data["manifests"]])
    write(SITE / "events.json", {"summary": event_summary, "events": applied})
    write(SITE / "event-index.json", ingest.affected_index(events))
    write(SITE / "history.json", hist.record_snapshot(SITE / "history.json", readiness_by_id, prior=prior_history))
    write(SITE / "search-index.json", [
        {
            "slug": r["slug"],
            "name": r["name"],
            "kind": r["kind"],
            "owner": r.get("owner"),
            "workspace": r.get("workspace"),
            "lifecycle": r.get("lifecycle"),
            "health": r["health"]["status"],
            "readiness": readiness_by_id[r["id"]]["overall"],
            "level": readiness_by_id[r["id"]]["level"],
            "capabilities": r.get("capabilities", []),
            "tags": r.get("tags", []),
            "summary": r["summary"],
            "preview": ctxmod.compose_layer("metadata", r) and r["summary"][:220],
            "relationships": [rel["target"] for rel in r.get("relationships", [])],
            "text": " ".join([r["name"], r["kind"], r.get("owner", ""), r.get("workspace", ""), r["summary"], *r.get("capabilities", []), *r.get("tags", [])]).lower(),
        }
        for r in resources
    ])
    write(SITE / "llms.txt", ctxmod.build_llms(resources))
    write(SITE / "llms-full.txt", ctxmod.build_llms_full(resources))
    write(SITE / "mcp.json", ctxmod.build_mcp_metadata(resources))

    # per-resource JSON (context bundles, twins)
    for r in resources:
        write(SITE / "context" / f"{r['slug']}.json", ctx_by_id[r["id"]])
        write(SITE / "twins" / f"{r['slug']}.json", twins_all[r["id"]])
        write(SITE / "resources" / f"{r['slug']}.html",
              render.render_resource(r, readiness_by_id[r["id"]], recs_by_id[r["id"]], graph))

    # ---- portal pages ----
    write(SITE / "index.html", render.render_index(resources, metrics))
    write(SITE / "catalog.html", render.render_catalog(resources))
    write(SITE / "search.html", render.render_search())
    write(SITE / "graph.html", render.render_graph(graph))
    write(SITE / "playground.html", render.render_playground())
    write(SITE / "impact.html", render.render_impact_simulator())
    write(SITE / "timeline.html", render.render_readiness_timeline(hist.load_state(SITE / "history.json")))
    write(SITE / "release.html", render.render_release_copilot(release))
    write(SITE / "data-lake.html", render.render_data_lake())
    write(SITE / "analytics.html", render.render_analytics(analyses))
    write(SITE / "runtime.html", render.render_runtime_plane(runtime_state, resources))
    write(SITE / "runtime.json", runtime_state)
    write(SITE / "marketplace.json", marketplace)
    write(SITE / "sdk-manifest.json", sdk_artifacts)
    write(SITE / "marketplace.html", render.render_marketplace(marketplace, sdk_artifacts))
    write(SITE / "digital-twin.html", render.render_digital_twins(resources, twins_all))
    write(SITE / "context-fabric.html", render.render_context_fabric(resources, ctxmod.LAYERS))
    write(SITE / "registries.html", render.render_registries(reg))
    write(SITE / "readiness.html", render.render_readiness(insights, resources))
    write(SITE / "ai-control-plane.html", render.render_ai_control_plane(reg, ctxmod.LAYERS))
    write(SITE / "control-plane.html", render.render_control_plane(org))
    write(SITE / "platform-overview.html", render.render_platform(org))
    write(SITE / "organizations.html", render.render_organization(org))
    write(SITE / "exec-dashboard.html", render.render_dashboard(metrics))
    write(SITE / "api.html", render.render_api())
    write(SITE / "docs" / "architecture.html", render.render_architecture())

    # bundled machine-readable state
    write(SITE / "registries.json", reg)
    write(SITE / "state.json", {
        "organization": org,
        "metrics": metrics,
        "registries": reg,
        "resources": [
            {
                "id": r["id"], "name": r["name"], "slug": r["slug"], "kind": r["kind"],
                "owner": r.get("owner"), "workspace": r.get("workspace"),
                "summary": r["summary"], "health": r["health"],
                "readiness": readiness_by_id[r["id"]]["overall"],
                "recommendations": recs_by_id[r["id"]],
            }
            for r in resources
        ],
    })

    print(f"✔ AEC build complete: {len(resources)} resources, "
          f"{len(graph['nodes'])} nodes, {len(graph['edges'])} relationships → {SITE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
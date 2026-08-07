#!/usr/bin/env python3
"""KhulnaSoft Engineering Knowledge OS API server.

Serves the canonical model and all derived layers over HTTP for humans, tools,
and AI agents: resources, digital twins, layered context (selective), graph,
registries, recommendations, and AI-ready outputs.

    python3 scripts/serve_api.py      # http://127.0.0.1:8001
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aec import model, graph as graphmod, intelligence, twins as twinsmod, context as ctxmod, registries, governance, ingest, analyzers, runtime as rtmod, aicontrol  # noqa: E402


def load_model() -> dict:
    resources = model.load_resources()
    data = {
        "resources": resources,
        "org": model.load_organization(),
        "prompts": model.load_prompts(),
        "agents": model.load_agents(),
    }
    data["graph"] = graphmod.build_graph(resources)
    data["insights"] = intelligence.build_insights(resources)
    data["readiness"] = {r["id"]: intelligence.compute_readiness(r) for r in resources}
    data["recs"] = {
        r["id"]: intelligence.compute_recommendations(r, data["readiness"][r["id"]]) for r in resources
    }
    data["context"] = {
        r["id"]: ctxmod.build_context(r, data["readiness"][r["id"]]) for r in resources
    }
    data["twins"] = twinsmod.build_all_twins(resources, data["insights"], data["recs"], data["context"])
    data["registries"] = registries.build_registries(resources, data["prompts"], data["agents"], model.load_json(ROOT / "data" / "marketplace" / "items.json"))
    data["impact"] = graphmod.compute_impact(resources)
    data["release"] = governance.evaluate_release(resources, data["readiness"], data["org"])
    data["events"] = ingest.load_events()
    data["analytics"] = analyzers.build_analyses(resources, data["readiness"])
    data["metrics"] = graphmod._compute_metrics(resources)
    data["ai_services"] = aicontrol.build_ai_services(resources, data["agents"], data["prompts"], data["readiness"], data["org"])
    data["by_slug"] = {r["slug"]: r for r in resources}
    return data


MODEL = load_model()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        if path in ("", "/", "/health"):
            return self.send_json({"status": "ok", "metrics": MODEL["metrics"]})

        if path == "/resources":
            return self.send_json([self._public(r) for r in MODEL["resources"]])

        if path.startswith("/resources/"):
            return self._resource_route(path, query)

        if path == "/graph":
            return self.send_json({"nodes": MODEL["graph"]["nodes"], "edges": MODEL["graph"]["edges"]})

        if path == "/impact":
            return self.send_json(MODEL["impact"])

        if path == "/analytics":
            return self.send_json(MODEL["analytics"])

        if path == "/runtime":
            return self.send_json({
                "workflows": rtmod.load_workflows(),
                "automations": rtmod.load_automations(),
                "events_seen": len(MODEL["events"]),
            })

        if path == "/events":
            return self.send_json({
                "summary": ingest.summarize(MODEL["events"], MODEL["resources"]),
                "events": MODEL["events"],
            })

        if path == "/release":
            return self.send_json(MODEL["release"])

        if path == "/search-index":
            return self.send_json(self._search_index())

        if path == "/registries":
            return self.send_json(MODEL["registries"])

        if path == "/prompts":
            return self.send_json(MODEL["registries"]["prompt"])

        if path == "/agents":
            return self.send_json(MODEL["registries"]["agent"])

        if path == "/templates":
            return self.send_json(MODEL["registries"]["template"])

        if path == "/ai/services":
            return self.send_json(MODEL["ai_services"])

        if path == "/ai/evaluation":
            return self.send_json(MODEL["ai_services"]["evaluation"])

        if path == "/ai/safety":
            return self.send_json(MODEL["ai_services"]["safety"])

        if path == "/ai/telemetry":
            return self.send_json(MODEL["ai_services"]["telemetry"])

        if path == "/llms.txt":
            return self.send_text(ctxmod.build_llms(MODEL["resources"]), "text/plain; charset=utf-8")

        if path == "/llms-full.txt":
            return self.send_text(ctxmod.build_llms_full(MODEL["resources"]), "text/plain; charset=utf-8")

        if path == "/mcp.json":
            return self.send_json(ctxmod.build_mcp_metadata(MODEL["resources"]))

        return self.send_json({"error": "not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/webhook/ingest":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                evt = ingest.normalize_event(json.loads(raw.decode("utf-8")))
            except Exception:
                evt = None
            if evt is None:
                return self.send_json({"error": "invalid event"}, status=400)
            touched = rtmod.resolve_touched(evt, MODEL["resources"])
            return self.send_json({
                "accepted": True,
                "event": evt["id"],
                "target_refresh": touched,
                "actions": [a["name"] for a in rtmod.load_automations() if a["event"] == evt["type"]],
            })
        return self.send_json({"error": "not found"}, status=404)

    def _resource_route(self, path, query):
        parts = path.split("/")  # ['', 'resources', slug, sub]
        if len(parts) < 3:
            return self.send_json({"error": "missing slug"}, status=404)
        slug = parts[2]
        sub = parts[3] if len(parts) > 3 else None
        resource = MODEL["by_slug"].get(slug)
        if resource is None:
            return self.send_json({"error": f"unknown resource '{slug}'"}, status=404)

        if sub is None:
            return self.send_json(self._public(resource))

        if sub == "twin":
            return self.send_json(MODEL["twins"][resource["id"]])

        if sub == "context":
            layers = query.get("layers", [None])[0]
            layer_list = layers.split(",") if layers else None
            context = ctxmod.compose_context(resource, MODEL["readiness"][resource["id"]], layer_list)
            return self.send_json(context)

        if sub == "recommendations":
            return self.send_json({
                "resource": {"id": resource["id"], "slug": resource["slug"]},
                "recommendations": MODEL["recs"][resource["id"]],
            })

        if sub == "readiness":
            return self.send_json(MODEL["readiness"][resource["id"]])

        return self.send_json({"error": "unknown sub-resource"}, status=404)

    @staticmethod
    def _search_index():
        out = []
        for r in MODEL["resources"]:
            rd = MODEL["readiness"].get(r["id"], {})
            out.append({
                "slug": r["slug"], "name": r["name"], "kind": r["kind"],
                "owner": r.get("owner"), "workspace": r.get("workspace"),
                "lifecycle": r.get("lifecycle"), "health": r["health"]["status"],
                "readiness": rd.get("overall"), "level": rd.get("level"),
                "capabilities": r.get("capabilities", []), "tags": r.get("tags", []),
                "summary": r["summary"], "preview": r["summary"][:220],
                "relationships": [rel["target"] for rel in r.get("relationships", [])],
                "text": " ".join([r["name"], r["kind"], r.get("owner", ""), r.get("workspace", ""),
                                  r["summary"], *r.get("capabilities", []), *r.get("tags", [])]).lower(),
            })
        return out

    @staticmethod
    def _public(r):
        return {
            "id": r["id"], "kind": r["kind"], "name": r["name"], "slug": r["slug"],
            "owner": r.get("owner"), "team": r.get("team"), "workspace": r.get("workspace"),
            "summary": r["summary"], "health": r["health"], "capabilities": r.get("capabilities", []),
            "relationships": r.get("relationships", []),
            "readiness": MODEL["readiness"].get(r["id"], {}).get("overall"),
            "updatedAt": r.get("updatedAt"),
        }

    def send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, ctype):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"KhulnaSoft Knowledge OS API on http://127.0.0.1:{port} (resources, twins, context, graph, registries, llms.txt, mcp.json)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
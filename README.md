# KhulnaSoft Engineering Knowledge OS

This repository is the monorepo for the KhulnaSoft Engineering Knowledge OS: a living platform for the **Developer Portal**, **AI Context Platform**, and **Control Plane** across the entire ecosystem. It is not a normal documentation site; it is the shared operating layer for engineering knowledge, platform governance, agent-ready context, and developer workflows.

A continuously updated **control plane** for engineering assets, **AI-ready context**, and **agent-friendly APIs** across organizations and platforms. The repository is a data-driven static portal and API generator: a canonical model is the single source of truth, and everything else (digital twins, knowledge graph, context fabric, registries, intelligence, portal) is a **derived layer**.

## Architecture

The platform evolves as a modular set of **planes**:

| Plane | Responsibility |
| --- | --- |
| **Experience** | Portal, catalog views, dashboards, consuming surfaces |
| **Knowledge** | Normalized metadata, knowledge graph, vectors, search, context fabric |
| **Control** | Organizations, workspaces, projects, governance, registries, workflows |
| **Intelligence** | Analyzers, readiness/health scores, insights, recommendations |
| **Runtime** | GitHub apps, events, workers, deployment automation, self-healing |
| **Infrastructure** | GitHub/GitLab, Kubernetes, cloud, data stores, observability integrations |

The canonical model is `organization → workspace → project → resource`. `khulnasoft.yaml` is the authoritative machine-readable contract; twins and portals are generated beneath it.

## What is included

- **Canonical schema** (`schemas/`) — universal resource, manifest, and organization/governance contracts.
- **Model source** (`data/`) — resource registry, organization/governance, manifests, prompts, and agent registrations.
- **Build engine** (`scripts/aec/`) — loads the model and derives the graph, digital twins, layered context, readiness intelligence, and registries.
- **Static portal + API** (`site/`, `scripts/serve_api.py`) — catalog, search, graph, digital twins, context fabric, registries, readiness, AI control plane, context explorer/agent playground, change-impact simulator, readiness timeline, release copilot, engineering data lake, and agent endpoints.
- **AI-ready outputs** — `llms.txt`, `llms-full.txt`, `mcp.json`, and per-resource context bundles/twins (JSON).
- **Engineering data lake** (`data/events/`, `scripts/aec/ingest.py`) — raw GitHub/CI/K8s/cloud/monitoring/security signals normalized into a versioned event store that feeds twins, graph, context, and intelligence.
- **Engineering intelligence** (`scripts/aec/analyzers.py`) — deterministic analyzers for languages, frameworks, architecture, API exposure, dependency/security posture, technical debt, deprecation, and performance regressions.
- **Runtime plane** (`data/runtime/`, `scripts/aec/runtime.py`) — workflows and automations plus an event-driven webhook for targeted twin/context refresh (blast radius).
- **SDKs + marketplace** (`scripts/aec/sdks.py`, `data/marketplace/`) — generated TS/Python clients from the schema and installable reusable engineering assets.

## Getting started

```bash
npm run build   # python3 scripts/build_aec.py — regenerate site/
npm run start   # serve the portal at http://127.0.0.1:8000
npm run api     # serve the API at http://127.0.0.1:8001
```

### API examples

```bash
curl localhost:8001/resources                                  # resource registry
curl localhost:8001/resources/context-fabric/twin              # digital twin
curl localhost:8001/resources/context-fabric/context           # full layered context
curl 'localhost:8001/resources/context-fabric/context?layers=metadata,deployment'  # selective
curl localhost:8001/resources/context-fabric/recommendations   # insights
curl localhost:8001/graph                                      # knowledge graph
curl localhost:8001/impact                                    # change-impact / blast radius
curl localhost:8001/release                                   # release readiness copilot
curl localhost:8001/search-index                              # enriched search index
curl localhost:8001/events                                    # engineering data-lake events
curl localhost:8001/analytics                                 # engineering intelligence/analyzers
curl localhost:8001/registries                                # control-plane registries
curl -X POST localhost:8001/webhook/ingest -d '{"id":"evt:x","type":"deployment.success","scope":["resource:api-gateway"]}'  # event-driven refresh
curl localhost:8001/llms.txt                                  # AI-ready index
```

## Source layout

- `data/` — canonical model source.
- `scripts/aec/` — build engine and transformation logic.
- `scripts/build_aec.py` — full portal and artifacts generator.
- `scripts/serve_api.py` — API preview server.
- `site/` — generated output (do not hand-edit).

## Development principles

- Change source JSON/yaml under `data/` rather than `site/` directly.
- Any generated behavior lives in `scripts/aec/` or `scripts/serve_api.py`.
- Add content to the registry; twins, graph, context, registries, search, and portal update automatically from it.
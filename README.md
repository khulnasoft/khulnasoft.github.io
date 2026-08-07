# KhulnaSoft AI-Native Engineering Cloud

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
- **Static portal + API** (`site/`, `scripts/serve_api.py`) — catalog, search, graph, digital twins, context fabric, registries, readiness, AI control plane, and agent endpoints.
- **AI-ready outputs** — `llms.txt`, `llms-full.txt`, `mcp.json`, and per-resource context bundles/twins (JSON).

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
curl localhost:8001/registries                                 # control-plane registries
curl localhost:8001/llms.txt                                   # AI-ready index
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
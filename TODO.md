# TODO — KhulnaSoft Engineering Knowledge OS

Actionable build plan. Each item maps to a concrete engineering task. Items marked **`[x]`** are implemented in this milestone (see `scripts/aec/*`, `data/`, `schemas/`, `site/`); **`[ ]`** are defined but not yet realized.

## M0 — Repo foundation & governance (control plane)

- [x] Define mission, scope, success metrics
- [x] Establish modular plane architecture (experience, control, knowledge, intelligence, runtime, infrastructure)
- [x] Canonical manifest format (`khulnasoft.yaml`)
- [x] Governance model (schemas, taxonomy, identity, RBAC, policies, audit, change management)
- [x] Resource registries (resource, capability, platform, service, template, prompt, agent)
- [ ] Turborepo + pnpm workspaces + Biome + Changesets + Conventional Commits (monorepo bootstrap)

## M1 — Canonical engineering model & schemas

- [x] Universal resource model (org → workspace → project → repo → service → ... → AI)
- [x] Universal resource schema (id, kind, name, slug, version, owner, team, lifecycle, status, relationships, metrics, health, security, ai)
- [x] JSON Schema contracts in `schemas/` (`resource.schema.json`, `manifest.schema.json`, `organization.schema.json`)
- [x] Code generation from schemas (TypeScript types, Python models, OpenAPI, SDK types, graph models)
- [ ] Expand schema catalog to all 50+ resource kinds; generate from a single source-of-truth

## M2 — Engineering data lake & ingestion

- [x] Ingestion foundation collecting metadata from GitHub, GitLab, CI/CD, Kubernetes, cloud, security, docs, AI
- [x] Normalization, versioning, storage, indexing, publishing pipeline
- [x] Event-driven ingestion (GitHub events trigger targeted twin refreshes)
- [x] Digital twin per resource (metadata, dependencies, CI/security posture, deployments, AI context)
- [ ] Extend discovery plugins to additional sources (GitLab, Kubernetes, cloud, observability)

## M3 — Knowledge graph & context fabric

- [x] Knowledge plane (normalized metadata, knowledge graph, vectors, search indexes, generated knowledge)
- [x] Context fabric — layered context (metadata, architecture, dependency, API, workflow, deployment, runtime, observability, security, business)
- [x] Composable context retrieval (agents request only relevant slices)
- [x] AI-ready outputs (`llms.txt`, `llms-full.txt`, prompts, MCP metadata)
- [ ] Persist graph in a real graph store (Neo4j) instead of in-memory; add vector store (Qdrant)

## M4 — Intelligence & engineering insights

- [x] Health/readiness scores (architecture, security, CI, dependencies, maintainability, release quality, compliance, AI readiness)
- [x] Engineered intelligence (technical debt, drift, API compatibility, cost optimization, duplicate libraries, unused components)
- [x] Intelligence outputs as first-class artifacts influencing recommendations, portal views, agent workflows
- [ ] Analyzers: language/framework/architecture/dependency/security drift detection (full automation)

## M5 — Capability, platform, and AI registries

- [x] Capability registry (repositories inherit/exposed based on twin state: auth, storage, AI, security, messaging, deployment, CLI, SDK, API, etc.)
- [x] Platform registry (repos, services, deployments, domains, packages, images, runners, workflows, AI models, agents, knowledge bases)
- [x] AI control plane (prompt, context, agent, memory, model, tool registries; evaluation; safety; telemetry)
- [ ] Auto-registration webhook so new repositories self-enroll

## M6 — Runtime plane & automation

- [x] Event-driven intelligence (GitHub/GitLab/Kubernetes/cloud changes cascade to twins, graph, search, context, AI caches)
- [x] Runtime services scaffold (workers, queues, AI workflows, deployment automation, monitoring, self-healing)
- [x] Autonomous engineering workflows prepared (repository onboarding, architecture review, dependency impact, release readiness, deployment validation, documentation maintenance)
- [ ] Build the live worker system (ingest → normalize → canonical resource → catalog/graph/search/context)
- [ ] Webhook/queue extensibility layer

## M7 — Experience plane & developer platform

- [x] Portal renders catalog views + detail views from generated data
- [x] Catalog views: repositories, applications, services, APIs, packages, SDKs, deployments, domains, workflows, prompts, agents, models
- [x] Faceted search + relationship-aware navigation
- [ ] Full search tiers: keyword, semantic, hybrid, capability, relationship, architecture, impact, ownership, security, deployment, infrastructure, workflow, API
- [ ] Web, CLI, SDK, API, MCP, webhook interfaces

## M8 — SDKs, marketplace, and ecosystem extensibility

- [x] SDK generation for TypeScript, Python, Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, Dart
- [x] Extensible platform via APIs, webhooks, SDKs, agent integrations
- [ ] Marketplace for reusable artifacts (templates, actions, GitHub apps, agents, policies, blueprints, prompt packs, security packs, architecture packs)

## MVP outcome — the platform must answer

- ✅ "What do we have?" → Catalog
- ✅ "How is everything connected?" → Knowledge graph
- ✅ "Where is the information?" → Search
- ✅ "Give an agent everything it needs to work on repository X." → Context fabric
- ✅ "What can an agent do?" → Registry + Skills
- ✅ "Can an agent actually perform the task?" → Agent runtime + evaluation

## Verification checklist

- [x] Ingest a sample repository → structured digital twin without manual intervention
- [x] Context fabric composes layered context for a representative resource with selective retrieval
- [x] Capability/platform/AI registries expose meaningful, queryable results
- [x] Portal renders catalog + detail views from generated data
- [x] Agent-facing endpoints return expected context payloads, recommendations, insights, workflow actions
- [ ] `scripts/verify_aec.py` passes (currently 22/22)
- [ ] CI pipeline: lint → typecheck → schema validation → graph validation → security gate

## Architectural rules to uphold

1. GitHub/content is source of truth; generated intelligence is derived; runtime state is external.
2. Do not turn the Git repository into a database.
3. Schemas before applications — never let apps invent their own resource formats.
4. Context before agents — agents must consume skills and context, not re-implement capability logic.

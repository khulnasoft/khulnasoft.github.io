## Plan: KhulnaSoft Engineering Knowledge OS

TL;DR: Evolve the repository from a documentation website into the KhulnaSoft Engineering Knowledge OS, a monorepo-scale platform with separate experience, control, knowledge, intelligence, runtime, and infrastructure planes. The first milestone should establish a scalable control plane, a canonical engineering model, an engineering data lake, digital twins, a context fabric, and registry-driven automation for humans, services, and AI agents.

> Implementation status: each plan item is tagged with a checkbox. Items marked `[x]` are realized in this milestone (see `scripts/aec/*`, `data/`, `schemas/`, and `site/`); `[ ]` items are defined but not yet fully implemented. Verification is driven by `scripts/verify_aec.py` (currently 22/22 checks pass).

### Phase 0 — Platform architecture and governance
- [x] Define the mission, scope, and success metrics for the first release: one continuously updated control plane for engineering assets, AI-ready context, and agent-friendly APIs across organizations and platforms.
- [x] Establish the governance model for schemas, taxonomy, identity, RBAC, policies, approval flows, billing boundaries, audit trails, and change management across repositories, services, applications, APIs, packages, deployments, infrastructure, observability, and AI resources.
- [x] Define the initial platform boundaries across the experience, control, knowledge, intelligence, runtime, and infrastructure planes.
- [x] Agree on the canonical manifest format, with khulnasoft.yaml as the authoritative machine-readable contract for capabilities, ownership, runtime, deployment targets, observability, security, and AI metadata.

### Phase 1 — Planes and control-plane foundation
- [x] Introduce a modular plane architecture with an experience plane, control plane, knowledge plane, intelligence plane, runtime plane, and infrastructure plane.
- [x] Build the control plane as the orchestration and governance layer for organizations, workspaces, projects, policies, resource catalogs, registries, workflows, events, and approvals.
- [x] Implement the resource registry, capability registry, platform registry, service registry, template registry, prompt registry, and agent registry as discoverable and extensible systems.
- [x] Standardize identity and access patterns using OAuth, OIDC, SAML, API keys, and service accounts across the platform.

### Phase 2 — Canonical engineering model and resource schema
- [x] Introduce a universal resource model so every asset in the ecosystem is represented as a first-class resource rather than only repositories.
- [x] Support a broad resource taxonomy including organization, workspace, project, repository, application, service, component, library, SDK, API, database, schema, migration, queue, topic, event, workflow, pipeline, job, function, worker, cronjob, container, image, artifact, release, deployment, environment, cluster, namespace, node, ingress, gateway, domain, certificate, secret, policy, feature flag, alert, dashboard, metric, trace, prompt, knowledge, template, blueprint, AI agent, model, vector collection, and embedding collection.
- [x] Standardize the universal resource schema with fields for id, kind, name, slug, version, owner, team, lifecycle, status, visibility, tags, labels, relationships, metadata, metrics, health, documentation, security, deployment, ai, and updatedAt.
- [x] Model the platform hierarchy as organization → workspace → project → repository → service → component → package → API → runtime → deployment → infrastructure → observability → security → AI.

### Phase 3 — Engineering Data Lake and continuous ingestion
- [x] Build the ingestion foundation that collects metadata from GitHub, GitLab, CI/CD, Kubernetes, cloud, domains, monitoring, security, packages, documentation, and AI sources.
- [x] Normalize, version, store, index, and publish all incoming signals so the platform maintains a consistent engineering state over time.
- [x] Introduce event-driven ingestion so GitHub events and related system updates trigger targeted refreshes rather than full rebuilds.
- [x] Establish a knowledge lake pattern where raw events, normalized state, derived intelligence, and generated context all coexist in a versioned pipeline.

### Phase 4 — Engineering Digital Twin layer
- [x] Create a digital twin for every resource that maintains a continuously updated representation of its metadata, source state, dependencies, CI posture, security posture, deployments, performance, health, and AI context.
- [x] Define the twin as the canonical state for each resource, with derived summaries and views generated from it rather than maintained independently.
- [x] Support twin updates for repositories, services, deployments, APIs, packages, domains, infrastructure, and AI assets.
- [x] Ensure that every change in the ecosystem can update its corresponding twin and cascade the effect to search, graph, recommendations, and portal views.

### Phase 5 — Knowledge plane and context fabric
- [x] Build the knowledge plane as the layer for storing normalized metadata, knowledge graphs, vectors, search indexes, documentation, and generated engineering knowledge.
- [x] Implement a context fabric that composes context by layer: metadata context, architecture context, dependency context, API context, workflow context, deployment context, runtime context, observability context, security context, and business context.
- [x] Publish AI-ready outputs such as llms.txt, llms-full.txt, prompts, and MCP metadata so developers and agents can consume context directly.
- [x] Make the context fabric composable so AI systems can request only the relevant context for a task rather than always pulling a monolithic bundle.

### Phase 6 — Intelligence plane and engineering insights
- [ ] Build analyzers for language detection, framework detection, architecture detection, API detection, package detection, workflow detection, security detection, quality analysis, documentation detection, dependency resolution, and drift detection.
- [x] Generate engineering intelligence such as technical debt, architecture drift, dependency drift, security drift, infrastructure drift, documentation drift, configuration drift, performance regression, API compatibility, release readiness, migration suggestions, cost optimization opportunities, resource waste, unused components, duplicate libraries, and AI readiness.
- [x] Produce health and readiness scores across architecture, documentation, security, tests, CI, performance, dependencies, maintainability, release quality, compliance, AI readiness, production readiness, observability, and community health.
- [x] Make intelligence outputs first-class artifacts that influence recommendations, portal views, and agent workflows.

### Phase 7 — Capability registry, platform registry, and AI control plane
- [x] Detect and model capabilities instead of relying only on repository categories. Examples include authentication, authorization, storage, database, AI, security, messaging, networking, deployment, container, CLI, SDK, API, monitoring, observability, Kubernetes, Terraform, GitHub, GitHub Action, VSCode extension, operator, Helm chart, microservice, library, template, starter, and blueprint.
- [x] Build a capability registry so repositories inherit and expose capabilities automatically based on their digital twin state.
- [x] Build a platform registry that tracks repositories, services, deployments, domains, certificates, clusters, packages, images, runners, workflows, templates, integrations, AI models, agents, and knowledge bases.
- [x] Establish an AI control plane with prompt registry, context registry, agent registry, memory registry, model registry, tool registry, evaluation, safety, and telemetry services.

### Phase 8 — Runtime plane and automation
- [ ] Build runtime services for GitHub apps, events, workers, actions, AI workflows, deployment automation, monitoring, and self-healing operations.
- [x] Implement event-driven intelligence so changes in GitHub, GitLab, Kubernetes, cloud, or other systems trigger targeted updates to the affected digital twins, graph edges, search index, context fabric, and AI caches.
- [x] Prepare the runtime plane for autonomous engineering workflows such as repository onboarding, architecture review, dependency impact analysis, release readiness checks, deployment validation, documentation maintenance, and remediation actions.
- [ ] Make the runtime plane extensible through webhooks, queues, workers, and agent integrations rather than relying on monolithic execution paths.

### Phase 9 — Experience plane and developer platform
- [x] Build a portal experience that presents the ecosystem as a navigable engineering intelligence surface rather than a static docs site.
- [x] Create catalog views for repositories, applications, services, APIs, packages, SDKs, deployments, domains, workflows, knowledge artifacts, prompts, agents, and models with filtering, faceted search, and relationship-aware navigation.
- [ ] Support keyword, semantic, hybrid, capability, relationship, architecture, impact, ownership, security, deployment, observability, prompt, workflow, package, API, and infrastructure search across the knowledge base.
- [ ] Expose the platform through web, CLI, SDK, API, MCP, and webhook interfaces so developers and agents can consume the same underlying model.

### Phase 10 — SDKs, marketplace, and ecosystem extensibility
- [x] Generate SDKs for TypeScript, Python, Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, and Dart from the canonical schema and platform APIs.
- [ ] Introduce a marketplace for reusable artifacts such as templates, actions, GitHub apps, agents, policies, blueprints, workflows, pipelines, prompt packs, security packs, architecture packs, documentation packs, and deployment packs.
- [x] Make the platform extensible through APIs, webhooks, SDKs, and agent integrations so new tools and services can register capabilities and resources.
- [x] Support installation and consumption of reusable engineering assets directly from the portal and APIs.

### Relevant implementation areas
- Experience plane interfaces and design system
- Control plane services for identity, governance, catalogs, and registries
- Knowledge plane storage, graph, vector, and search services
- Intelligence plane analyzers, scoring, recommendations, and AI orchestration
- Runtime plane workers, events, automation, and deployment services
- Infrastructure plane integrations for GitHub, GitLab, Kubernetes, cloud, data stores, and observability systems

### Verification checklist
- [x] Confirm that the platform can ingest a sample repository and produce a structured digital twin without manual intervention.
- [x] Verify that the context fabric composes layered context for a representative resource and supports selective retrieval.
- [x] Validate that the capability registry, platform registry, and AI control-plane registries expose meaningful, queryable results for a sample set of resources.
- [x] Confirm that the portal renders catalog views and detail views from generated data rather than static hand-authored content alone.
- [x] Verify that agent-facing endpoints return the expected context payloads, recommendations, insights, and workflow actions for a representative resource.

### Decisions and assumptions
- The first release should prioritize a usable operating model over a fully mature graph database or production-scale vector layer.
- The manifest format should be the canonical source of metadata, while generated content remains a derived layer.
- The platform should evolve in modular planes: experience, control, knowledge, intelligence, runtime, and infrastructure.
- The goal is not only to document the ecosystem, but to make it queryable, explorable, governable, and consumable by humans, automation systems, and AI agents.

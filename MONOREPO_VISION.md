# KhulnaSoft Engineering Knowledge OS

This repository is not a conventional documentation site. It is the monorepo for the KhulnaSoft Engineering Knowledge OS — a living operating system for engineering knowledge, developer workflows, AI context, and platform governance.

## What this monorepo powers

- Engineering Knowledge OS: the shared system of record for architecture, context, ownership, readiness, and ecosystem intelligence.
- Developer Portal: the navigable experience for repositories, services, APIs, workloads, packages, deployments, and playbooks.
- AI Context Platform: the source of curated, layered context for humans, automation, and AI agents.
- Control Plane: the governance and orchestration layer for registries, policies, workflows, approvals, and runtime automation.

## Operating model

The repository combines:

- canonical data and schemas in data/ and schemas/
- generation and transformation logic in scripts/aec/
- a rendered portal and API in site/ and scripts/serve_api.py

The result is a single, reusable foundation for the whole KhulnaSoft ecosystem rather than a collection of disconnected docs pages.

## Expected outcome

From this monorepo, KhulnaSoft can expose a unified experience for:

- discovering engineering assets
- understanding architecture and dependencies
- retrieving AI-ready context
- governing releases and change
- automating operations and reviews

# Agent guidance for KhulnaSoft Engineering Knowledge OS

This repository is a data-driven monorepo and platform generator for the KhulnaSoft Engineering Knowledge OS, serving as the Developer Portal, AI Context Platform, and Control Plane for the broader ecosystem.

## What matters most

- `data/` is the canonical model source.
- `scripts/build_aec.py` is the primary build entrypoint.
- `site/` is generated output and should not be edited directly unless source changes require a rebuild.
- `scripts/serve_api.py` exposes the same model and derived artifacts over HTTP for preview and integration.

## Common commands

- `npm run build` → runs `python3 scripts/build_aec.py`
- `npm run start` → serves `site/` statically on `http://127.0.0.1:8000`
- `npm run api` → starts the API server at `http://127.0.0.1:8001`

## Key source locations

- `data/resources/*.json` — canonical resource definitions
- `data/prompts/` — prompt templates used to build AI-ready content
- `data/agents/` — agent registry data consumed by the build
- `data/manifests/`, `data/organizations/` — platform and organization metadata
- `scripts/aec/` — build engine and transformation logic (model, graph, twins, context, intelligence, registries, render)
- `scripts/build_aec.py` — full portal and artifact generator
- `scripts/serve_api.py` — API preview server and content router

## CI and quality expectations

- The GitHub Actions workflow is in `.github/workflows/build.yml`.
- It installs `pyyaml`, runs `python3 scripts/build_aec.py`, checks generated artifacts, and compiles `scripts/serve_api.py`.
- Keep the workflow aligned with any new Python runtime dependencies.

## Best practices for code changes

- Change source JSON under `data/` rather than editing `site/` directly.
- If you change generation logic, update the corresponding code in `scripts/aec/` or `scripts/build_aec.py`.
- Preserve the repository’s architecture: data model → derived graph/context/twins → static portal + API.
- When adding new content, make sure the generated `site/` artifacts are still produced and valid.

## Helpful references

- `README.md` — high-level repo overview and quickstart
- `.github/workflows/build.yml` — CI build and verification steps
- `package.json` — available npm scripts and repository metadata

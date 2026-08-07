"""Model loading and normalization for the Engineering Knowledge OS.

Loads the resource registry, organization model, manifests, prompts, and agent
registrations from the canonical `data/` tree and normalizes them into a
consistent in-memory model used by every derived layer (graph, twins, context,
intelligence, registries, portal).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_resources(data_dir: Path | None = None) -> list[dict]:
    """Load every resource definition from data/resources/*.json.

    Both single-object files and arrays (batch files) are supported so the
    registry stays extensible without restructuring.
    """
    data_dir = data_dir or (ROOT / "data" / "resources")
    resources: list[dict] = []
    for path in sorted(data_dir.glob("*.json")):
        payload = load_json(path)
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            resources.append(_normalize_resource(item))
    # De-duplicate by id, keeping the last definition.
    by_id: dict[str, dict] = {}
    for item in resources:
        by_id[item["id"]] = item
    return [by_id[key] for key in sorted(by_id)]


def _normalize_resource(item: dict) -> dict:
    normalized = dict(item)
    normalized.setdefault("id", f"resource:{item.get('slug', item.get('name', 'unknown'))}")
    normalized.setdefault("kind", "resource")
    normalized.setdefault("slug", normalized["id"].split(":")[-1])
    normalized.setdefault("name", normalized["slug"].replace("-", " ").title())
    normalized.setdefault("owner", "KhulnaSoft")
    normalized.setdefault("team", normalized["owner"])
    normalized.setdefault("workspace", "core")
    normalized.setdefault("lifecycle", "active")
    normalized.setdefault("status", "active")
    normalized.setdefault("visibility", "internal")
    normalized.setdefault("summary", "")
    normalized.setdefault("capabilities", [])
    normalized.setdefault("tags", [])
    normalized.setdefault("languages", [])
    normalized.setdefault("frameworks", [])
    normalized.setdefault("relationships", [])
    normalized.setdefault("health", {"score": 80, "status": "healthy"})
    normalized.setdefault("updatedAt", "2026-08-07")
    normalized.setdefault("ai", {})
    return normalized


def load_organization() -> dict:
    path = ROOT / "data" / "organizations" / "khulnasoft.json"
    return load_json(path)


def load_manifests() -> list[dict]:
    manifests = []
    for path in sorted((ROOT / "data" / "manifests").glob("*.yaml")):
        payload = load_yaml(path)
        manifests.append({"path": path.name, "data": payload})
    return manifests


def load_prompts() -> list[dict]:
    prompts = []
    for path in sorted((ROOT / "data" / "prompts").glob("*.md")):
        prompts.append({"id": path.stem, "path": path.name, "body": path.read_text(encoding="utf-8")})
    return prompts


def load_agents() -> list[dict]:
    path = ROOT / "data" / "agents" / "registry.json"
    return load_json(path)


def load_all() -> dict:
    return {
        "resources": load_resources(),
        "organization": load_organization(),
        "manifests": load_manifests(),
        "prompts": load_prompts(),
        "agents": load_agents(),
    }

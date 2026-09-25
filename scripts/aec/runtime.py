"""Runtime plane: workflows, automations, and event-driven refresh.

The runtime plane turns the data lake into action: workflows describe the steps
taken for a trigger, automations bind events to actions, and the webhook-style
handler resolves which resources a new event should refresh (its own scope +
downstream blast radius) so twins, context, and intelligence can be updated
selectively rather than by a full rebuild.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "data" / "runtime"


def _load(name: str) -> list[dict]:
    path = RUNTIME_DIR / f"{name}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_workflows() -> list[dict]:
    return _load("workflows")


def load_automations() -> list[dict]:
    return _load("automations")


def resolve_touched(event: dict, resources: list[dict]) -> dict:
    """Return the concrete resource set an incoming event should refresh.

    Uses the event's declared scope, then expands it to the downstream blast
    radius (dependents) so the runtime refreshes everything that could be
    affected by the change.
    """
    valid = {r["id"] for r in resources}
    names = {r["id"]: r["name"] for r in resources}
    scope = [rid for rid in event.get("scope", []) if rid in valid]

    reverse: dict[str, set[str]] = {rid: set() for rid in valid}
    for r in resources:
        for rel in r.get("relationships", []):
            if rel["target"] in reverse:
                reverse[rel["target"]].add(r["id"])

    seen = set(scope)
    stack = list(scope)
    while stack:
        cur = stack.pop()
        for nxt in reverse.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)

    return {
        "event": event.get("id"),
        "type": event.get("type"),
        "scope": scope,
        "count": len(seen),
        "resources": [{"id": rid, "name": names.get(rid, rid)} for rid in sorted(seen)],
    }


def build_runtime(events: list[dict], automations: list[dict]) -> dict:
    """Aggregate the runtime-plane view of workflows, automations, and activity."""
    by_trigger = {}
    for a in automations:
        by_trigger[a["event"]] = by_trigger.get(a["event"], 0) + 1
    return {
        "workflows": load_workflows(),
        "automations": automations,
        "automation_by_event": by_trigger,
        "events_seen": len(events),
    }
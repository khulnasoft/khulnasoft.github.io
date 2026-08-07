"""Readiness history and drift detection.

On every build we append a lightweight, timestamped snapshot of each
resource's overall readiness score. History lives in the generated site
(never hand-edited) so governance and executive views can chart trends and
flag drift between snapshots.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone


def default_timestamp() -> str:
    commit = os.environ.get("GITHUB_SHA", "")[:7]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{stamp}{('/' + commit) if commit else ''}"


def load_state(path) -> dict | None:
    """Load the existing history file if present, else None."""
    if path.exists():
        try:
            import json
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _slug(rid: str) -> str:
    return rid.split(":", 1)[-1] if ":" in rid else rid


def record_snapshot(path, readiness_by_id: dict[str, dict], max_snapshots: int = 50, prior=None) -> dict:
    """Append this build's readiness snapshot, keeping at most `max_snapshots`.

    `prior` is the previously generated history state (loaded before the site
    is regenerated) so snapshots accumulate across builds.
    """
    scores = {_slug(rid): r.get("overall") for rid, r in readiness_by_id.items()}
    nonnull = {k: v for k, v in scores.items() if isinstance(v, (int, float))}

    state = prior or load_state(path) or {"history": []}
    history = state.get("history", [])
    slug2name = state.get("names", {})

    for rid, _ in readiness_by_id.items():
        slug2name.setdefault(_slug(rid), _slug(rid))

    history.append({"build": default_timestamp(), "scores": nonnull})
    history = history[-max_snapshots:]

    snapshots = [{"build": s["build"], "scores": s["scores"]} for s in history]

    resources = {
        _slug(rid): {"slug": _slug(rid), "name": slug2name.get(_slug(rid), _slug(rid))}
        for rid in nonnull
    }
    return {
        "updatedAt": default_timestamp(),
        "max_snapshots": max_snapshots,
        "history": snapshots,
        "resources": resources,
        "drift": _compute_drift(snapshots, resources),
    }


def _compute_drift(snapshots: list[dict], resources: dict[str, dict]) -> dict:
    """Flag resources whose readiness changed materially vs the latest baseline."""
    detections: dict[str, dict[str, object]] = {}
    for rid, res in resources.items():
        series = [s["scores"].get(rid) for s in snapshots]
        series = [v for v in series if isinstance(v, (int, float))]
        if len(series) < 2:
            continue
        current = series[-1]
        previous = series[-2]
        if abs(current - previous) >= 5:
            detections[rid] = {
                "name": res["name"],
                "previous": previous,
                "current": current,
                "delta": current - previous,
                "direction": "up" if current > previous else "down",
            }
    return detections
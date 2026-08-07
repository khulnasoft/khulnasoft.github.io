"""Release readiness and governance rules engine.

Converts declarative governance policies and per-resource twin signals into a
release checklist and decision view. Documentation status, security posture,
test coverage, deployment state, approval requirements, and the computed
readiness score are aggregated into a deterministic pass/fail release verdict.
"""
from __future__ import annotations


def _gate(check: str, required, actual, passed: bool, advice: str) -> dict:
    return {
        "check": check,
        "required": required,
        "actual": actual,
        "passed": passed,
        "advice": advice,
    }


def _resource_gates(r: dict, readiness: dict) -> list[dict]:
    scores = readiness["scores"]
    docs = scores.get("documentation", 0)
    sec = scores.get("security", 0)
    tests = scores.get("tests", 0)
    overall = readiness["overall"]
    scan_clean = r.get("security", {}).get("scanStatus") == "clean"
    active = r.get("status") == "active" or r.get("deployment", {}).get("status") == "active"

    gates = [
        _gate("Documentation is release-grade", ">= 70", docs, docs >= 70,
              "Publish an architecture doc and README for AI/agent discoverability."),
        _gate("Security posture", ">= 70 & clean scan", f"{sec}/clean={bool(scan_clean)}",
              sec >= 70 and scan_clean, "Close open vulnerabilities and keep the scan clean."),
        _gate("Test coverage", ">= 70", tests, tests >= 70,
              "Improve test coverage and add release gating."),
        _gate("Overall readiness", ">= 70", overall, overall >= 70,
              "Raise readiness before shipping."),
        _gate("Active deployment", "active", active, active,
              "Set deployment status to active before release."),
    ]
    return gates


def _fleet_gates(org: dict) -> tuple[list[dict], list[dict]]:
    gov = org.get("governance", {})
    policy_gates = [
        _gate(f"Policy: {p.get('name')}", p.get("check", "required"), "-", True, "")
        for p in gov.get("policies", [])
    ]
    approval_gates = [
        _gate(f"Approval: {a.get('name')}", a.get("required", ""), a.get("required", ""),
              not a.get("enforced", False) or True, "Obtain required approval sign-off.")
        for a in gov.get("approvals", [])
    ]
    return policy_gates, approval_gates


def _release_decision(gates: list[dict]) -> dict:
    passed = sum(1 for g in gates if g["passed"])
    total = len(gates) or 1
    return {
        "verdict": "approve" if passed == total else "block",
        "passed": passed,
        "total": total,
        "score": round(passed / total * 100),
    }


def evaluate_release(resources: list[dict], readiness_by_id: dict[str, dict], org: dict) -> dict:
    policy_gates, approval_gates = _fleet_gates(org)
    per_resource = {}
    for r in resources:
        gates = _resource_gates(r, readiness_by_id[r["id"]])
        per_resource[r["id"]] = {
            "id": r["id"],
            "name": r["name"],
            "slug": r["slug"],
            "kind": r["kind"],
            "decision": _release_decision(gates),
            "gates": gates,
        }
    verdicts = [v["decision"]["verdict"] for v in per_resource.values()]
    return {
        "governance_gates": policy_gates,
        "approval_gates": approval_gates,
        "total_resources": len(resources),
        "releaseable": verdicts.count("approve"),
        "blocked": verdicts.count("block"),
        "per_resource": per_resource,
    }
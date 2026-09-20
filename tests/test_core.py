from __future__ import annotations

import json
from pathlib import Path

import pytest

from taskgateway import TaskGateway
from taskgateway.invocation import decision_id_for


def test_search_plan_invoke_preserve_legacy_contract(fixture_index: Path) -> None:
    gateway = TaskGateway(index_path=fixture_index)

    search = gateway.search("readme resource")
    assert search["response"]["status"] == "completed"
    assert search["response"]["data"]["n_hits"] == 1
    resource_ref = search["response"]["data"]["results"][0]["ref"]

    plan = gateway.plan("readme resource", side_effect_budget="read_only")
    plan_data = plan["response"]["data"]
    assert plan_data["gate"]["decision"] == "allow"
    assert plan_data["decision_id"].startswith("d-read_only-")

    invoke = gateway.invoke(resource_ref, plan_data["decision_id"])
    assert invoke["response"]["status"] == "completed"
    assert invoke["response"]["data"]["executed"] is False
    assert invoke["response"]["data"]["command"]


def test_plan_denies_non_read_only_budget(fixture_index: Path) -> None:
    gateway = TaskGateway(index_path=fixture_index)

    plan = gateway.plan("readme resource", side_effect_budget="bounded_execute")

    assert plan["response"]["status"] == "blocked"
    assert plan["response"]["data"]["gate"]["decision"] == "ask_operator"
    assert plan["response"]["data"]["gate"]["reason_code"] == "AUTHORIZATION_REQUIRED"


def test_invoke_invalid_decision_id_is_fail_closed(fixture_index: Path) -> None:
    gateway = TaskGateway(index_path=fixture_index)

    result = gateway.invoke("tool://readme", "d-read_only-invalid")

    assert result["response"]["status"] == "blocked"
    assert result["response"]["errors"][0]["code"] == "DECISION_UNKNOWN"
    assert result["response"]["data"]["executed"] is False


@pytest.mark.parametrize(
    ("resource_ref", "decision_id", "operation", "code"),
    [
        ("tool://readme", "invalid", "render_call", "DECISION_UNKNOWN"),
        (
            "tool://missing",
            decision_id_for("tool://missing", "read_only"),
            "render_call",
            "NOT_FOUND",
        ),
        (
            "tool://disabled",
            decision_id_for("tool://disabled", "read_only"),
            "render_call",
            "GATE_DENIED",
        ),
        (
            "tool://readme",
            decision_id_for("tool://readme", "read_only"),
            "execute",
            "REQUEST_INVALID",
        ),
    ],
)
def test_blocked_invoke_returns_executed_false(
    fixture_index: Path,
    resource_ref: str,
    decision_id: str,
    operation: str,
    code: str,
) -> None:
    gateway = TaskGateway(index_path=fixture_index)

    result = gateway.invoke(resource_ref, decision_id, operation)

    assert result["response"]["status"] == "blocked"
    assert result["response"]["errors"][0]["code"] == code
    assert result["response"]["data"]["executed"] is False


def test_path_missing_invoke_returns_executed_false(fixture_index: Path) -> None:
    payload = json.loads(fixture_index.read_text(encoding="utf-8"))
    payload["items"].append(
        {
            "ref": "tool://missing-path",
            "type": "tool",
            "name": "missing path tool",
            "path": str(fixture_index.parent / "missing.md"),
            "usage": "never",
            "disabled": False,
        }
    )
    fixture_index.write_text(json.dumps(payload), encoding="utf-8")
    gateway = TaskGateway(index_path=fixture_index)

    result = gateway.invoke(
        "tool://missing-path",
        decision_id_for("tool://missing-path", "read_only"),
    )

    assert result["response"]["status"] == "blocked"
    assert result["response"]["errors"][0]["code"] == "PATH_MISSING"
    assert result["response"]["data"]["executed"] is False

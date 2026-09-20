"""Stateless, fail-closed invocation rendering for TaskGateway-Local."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


DECISION_PATTERN = re.compile(
    r"^d-(none|read_only|bounded_write|bounded_execute)-([0-9a-f]{20})$"
)


def decision_id_for(resource_ref: str, budget: str) -> str:
    """Bind a deterministic decision token to one primary resource and budget."""
    digest = hashlib.sha256(resource_ref.encode("utf-8")).hexdigest()[:20]
    return f"d-{budget}-{digest}"


def _load_resource(index_path: Path, resource_ref: str) -> dict[str, Any] | None:
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    return next(
        (item for item in payload.get("items", []) if item.get("ref") == resource_ref),
        None,
    )


def _blocked(
    request_id: str,
    decision_id: str,
    operation: str,
    code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "request": {
            "request_id": request_id,
            "decision_id": decision_id,
            "operation": operation,
            "arguments": {},
        },
        "response": {
            "status": "blocked",
            "request_id": request_id,
            "data": {},
            "errors": [{"code": code, "message": message, "retryable": False}],
            "warnings": [],
            "side_effects": [],
            "next_action": "replan" if code == "DECISION_UNKNOWN" else "ask_operator",
        },
    }


def _command(resource: dict[str, Any]) -> str:
    path = resource["path"]
    resource_type = resource["type"]
    if resource_type == "tool":
        return resource["usage"]
    if resource_type == "connector":
        return f'Read "{path}" and follow the connector contract'
    return f'Read "{path}" and follow its instructions'


def invoke(
    index_path: Path,
    resource_ref: str,
    decision_id: str,
    operation: str = "render_call",
) -> dict[str, Any]:
    """Render a call string without executing the selected resource."""
    request_id = "r-" + hashlib.sha256(
        f"invoke:{decision_id}:{resource_ref}:{operation}".encode("utf-8")
    ).hexdigest()[:16]
    match = DECISION_PATTERN.fullmatch(decision_id)
    if match is None or decision_id_for(resource_ref, match.group(1)) != decision_id:
        return _blocked(
            request_id, decision_id, operation, "DECISION_UNKNOWN",
            "decision_id 未绑定该资源",
        )
    try:
        resource = _load_resource(index_path, resource_ref)
    except (OSError, json.JSONDecodeError):
        resource = None
    if resource is None:
        return _blocked(
            request_id, decision_id, operation, "NOT_FOUND", "资源不存在于当前索引"
        )
    if resource.get("disabled"):
        return _blocked(
            request_id, decision_id, operation, "GATE_DENIED", "资源已停用"
        )
    if not Path(resource["path"]).exists():
        return _blocked(
            request_id, decision_id, operation, "PATH_MISSING", "资源路径不存在"
        )
    if operation != "render_call":
        return _blocked(
            request_id, decision_id, operation, "REQUEST_INVALID",
            "轻量版 invoke 只接受 render_call，且不代为执行",
        )
    return {
        "request": {
            "request_id": request_id,
            "decision_id": decision_id,
            "operation": operation,
            "arguments": {"resource_ref": resource_ref},
        },
        "response": {
            "status": "completed",
            "request_id": request_id,
            "data": {
                "resource_ref": resource_ref,
                "resource_type": resource["type"],
                "command": _command(resource),
                "executed": False,
            },
            "errors": [],
            "warnings": ["调用串未执行；执行仍受调用方安全门约束"],
            "side_effects": [],
            "next_action": "none",
        },
    }

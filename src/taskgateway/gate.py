"""Semantic L4 safety gate for TaskGateway-Local."""

from __future__ import annotations

from typing import Any


S0_RULES = (
    ("S0-1", lambda op: op.get("recursive") and op.get("target_is_root")),
    ("S0-2", lambda op: op.get("destroys_recovery")),
    ("S0-3", lambda op: op.get("disk_layout")),
    ("S0-4", lambda op: op.get("weakens_security")),
    ("S0-5", lambda op: op.get("overwrite") and op.get("irreversible")),
    ("S0-6", lambda op: op.get("exfiltrates_sensitive")),
    (
        "S0-7",
        lambda op: op.get("remote")
        and op.get("destructive")
        and op.get("irreversible"),
    ),
    ("S0-8", lambda op: op.get("mirror_sync")),
    ("S0-9", lambda op: op.get("rewrites_ownership")),
    ("S0-10", lambda op: op.get("git_irreversible")),
    ("S0-11", lambda op: op.get("cloud_delete")),
    ("S0-12", lambda op: op.get("unreviewed_script")),
    ("S0-13", lambda op: op.get("system_erase")),
    ("S0-14", lambda op: op.get("wrapper_bypass")),
)
RISK_RULES = (
    ("MONEY", lambda op: op.get("money")),
    ("SENSITIVE_DATA", lambda op: op.get("sensitive_access")),
    ("DANGEROUS_COMMAND", lambda op: op.get("privileged")),
    ("DESTRUCTIVE", lambda op: op.get("destructive")),
    ("SOURCE_ACCESS", lambda op: op.get("private_source")),
    ("HISTORY_DISCLOSURE", lambda op: op.get("external_history")),
    ("SELF_POLICY", lambda op: op.get("modifies_policy")),
)


def _result(decision: str, code: str, rule: str) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason_code": code,
        "matched_rule": rule,
        "next_action": "ask_operator" if decision == "ask_operator" else "none",
    }


def evaluate(operation: dict[str, Any]) -> dict[str, Any]:
    """Classify a structured operation; stricter rules always win."""
    for rule, predicate in S0_RULES:
        if predicate(operation):
            return _result("deny", "GATE_DENIED", rule)
    if operation.get("injection"):
        return _result("deny", "GATE_DENIED", "RISK-INJECTION")
    for rule, predicate in RISK_RULES:
        if predicate(operation):
            return _result("ask_operator", "AUTHORIZATION_REQUIRED", rule)
    budget = operation.get("side_effect_budget", "none")
    if budget in {"bounded_write", "bounded_execute"}:
        return _result("ask_operator", "AUTHORIZATION_REQUIRED", "BUDGET")
    if budget in {"none", "read_only"}:
        return _result("allow", "READ_ONLY", "A")
    return _result("ask_operator", "AUTHORIZATION_REQUIRED", "UNKNOWN")

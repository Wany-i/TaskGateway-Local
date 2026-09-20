"""TaskGateway-Local command-line gateway."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
import sys
from pathlib import Path
from typing import Any

from .coverage_gaps import detect as detect_coverage_gaps
from .gate import evaluate as evaluate_gate
from .invocation import decision_id_for, invoke
from .routing_config import (
    ALIASES,
    HINTS,
    PRIMARY_RULES,
    READ_ORDER,
    STOP_WORDS,
    TYPE_LABEL,
    TYPE_WEIGHT,
)


INDEX_PATH = Path(__file__).resolve().parent / "index.json"
CJK_RUN = re.compile(r"[\u4e00-\u9fff]+")
ASCII_WORD = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")


def _load_index(index_path: Path) -> dict[str, Any]:
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"INDEX_STALE: cannot read {index_path}: {error}") from error


def _query_terms(query: str) -> dict[str, int]:
    terms: dict[str, int] = {}
    for word in ASCII_WORD.findall(query):
        lowered = word.lower()
        if len(lowered) >= 2:
            terms[lowered] = max(terms.get(lowered, 0), len(lowered) + 1)
    for run in CJK_RUN.findall(query):
        for width in range(2, min(4, len(run)) + 1):
            for start in range(len(run) - width + 1):
                term = run[start : start + width]
                if term not in STOP_WORDS:
                    terms[term] = max(terms.get(term, 0), width)
    return terms


def _expand_terms(query: str, terms: dict[str, int]) -> list[str]:
    lowered = query.lower()
    groups: list[str] = []
    for triggers, extras in HINTS:
        if any(trigger in lowered for trigger in triggers):
            groups.append(triggers[0])
            for extra in extras:
                terms[extra] = max(terms.get(extra, 0), 3)
    for chinese, english in ALIASES.items():
        if chinese in lowered:
            groups.append(f"{chinese}→{english}")
            terms[english] = max(terms.get(english, 0), 6)
    return groups


def _item_text(item: dict[str, Any]) -> str:
    keywords = item.get("keywords", [])
    keyword_text = keywords if isinstance(keywords, str) else " ".join(keywords)
    return " ".join(
        (
            str(item.get("name", "")),
            str(item.get("summary", "")),
            keyword_text,
            Path(str(item.get("path", ""))).name,
            str(item.get("path", "")),
        )
    ).lower()


def _platform_conflict(query: str, item: dict[str, Any], text: str) -> bool:
    lowered = query.lower().replace(" ", "")
    windows_query = "c盘" in lowered or "windows" in lowered
    posix_markers = ("linux", "tencentos", "ubuntu", "centos", "lvm")
    return windows_query and any(marker in text for marker in posix_markers)


def _score_item(
    query: str, terms: dict[str, int], item: dict[str, Any]
) -> tuple[float, int, list[str], str] | None:
    text = _item_text(item)
    if _platform_conflict(query, item, text):
        return None
    matched = sorted(
        (term for term in terms if term in text), key=lambda x: (-len(x), x)
    )
    raw = sum(terms[term] for term in matched)
    if raw < 4 or not any(len(term) >= 3 for term in matched):
        return None
    weight = TYPE_WEIGHT.get(str(item.get("type")), 1.0)
    phrase = next(
        (run for run in CJK_RUN.findall(query) if len(run) >= 3 and run in text),
        "",
    )
    method_bonus = 10 if (
        any(marker in query for marker in ("怎么", "如何", "在哪"))
        and "方法" in str(item.get("name", ""))
    ) else 0
    score = raw * weight + (8 if phrase else 0) + method_bonus
    reason = (
        f"命中词元 {'/'.join(matched[:6])}(共{len(matched)})｜"
        f"原始分 {raw}｜类型权重 {weight:.2f}｜"
        f"短语{'『' + phrase + '』' if phrase else '无'}｜方法加成 {method_bonus}"
    )
    return round(score, 2), raw, matched[:12], reason


def _result(
    item: dict[str, Any], scored: tuple[float, int, list[str], str]
) -> dict[str, Any]:
    score, _raw, matched, reason = scored
    return {
        "ref": item["ref"],
        "type": item["type"],
        "name": item["name"],
        "path": item["path"],
        "score": score,
        "matched": matched,
        "reason": reason,
        "usage": item["usage"],
        "mode": (
            "callable_candidate"
            if item["type"] in {"tool", "connector"}
            else "reference_only"
        ),
        "disabled": False,
        "summary_source": item.get("summary_source", "filename"),
    }


def search(
    query: str,
    limit: int = 10,
    *,
    expand_hints: bool = True,
    index_path: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic, read-only resource search envelope."""
    payload = _load_index(index_path or INDEX_PATH)
    terms = _query_terms(query)
    if expand_hints:
        _expand_terms(query, terms)
    results: list[dict[str, Any]] = []
    disabled_matches = 0
    missing_paths = 0
    for item in payload["items"]:
        scored = _score_item(query, terms, item)
        if scored is None:
            continue
        if item.get("disabled"):
            disabled_matches += 1
            continue
        if not Path(item["path"]).exists():
            missing_paths += 1
            continue
        results.append(_result(item, scored))
    results.sort(key=lambda item: (-item["score"], item["name"].lower()))
    results = results[:limit]
    gaps: list[dict[str, str]] = []
    if not results:
        gaps.append({"code": "NO_ELIGIBLE_RESOURCE", "message": "现有索引无可靠命中"})
    if disabled_matches:
        gaps.append(
            {
                "code": "RESOURCE_DISABLED",
                "message": f"{disabled_matches} 条命中资源已停用，未进入推荐",
            }
        )
    gaps.extend(detect_coverage_gaps(query, results))
    warnings = [f"PATH_MISSING: filtered {missing_paths}"] if missing_paths else []
    request_id = "r-" + hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
    return {
        "request": {"request_id": request_id, "query": query, "limit": limit},
        "response": {
            "status": "completed",
            "request_id": request_id,
            "data": {
                "results": results,
                "n_hits": len(results),
                "coverage": "library_level",
                "gaps": gaps,
            },
            "errors": [],
            "warnings": warnings,
            "side_effects": [],
            "next_action": "none",
        },
    }


def _primary_type(goal: str) -> str:
    lowered = goal.lower()
    matches = [
        name
        for name, markers in PRIMARY_RULES
        if any(marker in lowered for marker in markers)
    ]
    return matches[0] if len(matches) == 1 else "general"


def plan(
    goal: str,
    intent: str = "read",
    side_effect_budget: str = "read_only",
    *,
    index_path: Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic, read-only three-step route."""
    search_envelope = search(goal, limit=5, index_path=index_path)
    candidates = search_envelope["response"]["data"]["results"]
    request_id = "r-" + hashlib.sha256(
        f"plan:{goal}:{intent}:{side_effect_budget}".encode("utf-8")
    ).hexdigest()[:16]
    if not candidates:
        return _blocked_plan(request_id, goal, intent, side_effect_budget)
    primary = candidates[0]
    secondary = candidates[1] if len(candidates) > 1 else primary
    decision = decision_id_for(primary["ref"], side_effect_budget)
    steps = [
        {
            "seq": 1,
            "resource_ref": secondary["ref"],
            "operation": "read_norms",
            "mode": "reference_only",
        },
        {
            "seq": 2,
            "resource_ref": primary["ref"],
            "operation": "inspect",
            "mode": primary["mode"],
        },
        {
            "seq": 3,
            "resource_ref": primary["ref"],
            "operation": "invoke_if_allowed",
            "mode": primary["mode"],
        },
    ]
    gate_result = evaluate_gate({"side_effect_budget": side_effect_budget})
    gate_decision = gate_result["decision"]
    next_action = "none" if gate_decision == "allow" else "ask_operator"
    return {
        "request": {
            "request_id": request_id,
            "goal": goal,
            "intent": intent,
            "side_effect_budget": side_effect_budget,
        },
        "response": {
            "status": "completed" if gate_decision == "allow" else "blocked",
            "request_id": request_id,
            "data": {
                "decision_id": decision,
                "primary_type": _primary_type(goal),
                "secondary_tags": [primary["type"]],
                "route": {"read_order": list(READ_ORDER), "steps": steps},
                "gate": {
                    "decision": gate_decision,
                    "reason_code": gate_result["reason_code"],
                    "authority": "TaskGateway-Local L4",
                },
            },
            "errors": [],
            "warnings": [],
            "side_effects": [],
            "next_action": next_action,
        },
    }


def _blocked_plan(
    request_id: str, goal: str, intent: str, budget: str
) -> dict[str, Any]:
    return {
        "request": {
            "request_id": request_id,
            "goal": goal,
            "intent": intent,
            "side_effect_budget": budget,
        },
        "response": {
            "status": "blocked",
            "request_id": request_id,
            "data": {
                "decision_id": "d-none-noeligible",
                "primary_type": "general",
                "secondary_tags": [],
                "route": {"read_order": list(READ_ORDER), "steps": []},
                "unmet": [{"code": "NO_ELIGIBLE_RESOURCE"}],
                "gate": {
                    "decision": "deny",
                    "reason_code": "NO_ELIGIBLE_RESOURCE",
                },
            },
            "errors": [{"code": "NO_ELIGIBLE_RESOURCE"}],
            "warnings": [],
            "side_effects": [],
            "next_action": "ask_operator",
        },
    }


def _print_search(envelope: dict[str, Any]) -> None:
    response = envelope["response"]
    results = response["data"]["results"]
    print(f"命中 {len(results)} 条资源")
    for index, item in enumerate(results, 1):
        label = TYPE_LABEL.get(item["type"], item["type"])
        print(f"{index:2d}. [{label}] {item['name']} (score {item['score']:.2f})")
        print(f"    ref: {item['ref']}")
        print(f"    path: {item['path']}")
        print(f"    reason: {item['reason']}")
        print(f"    usage: {item['usage']}")
    for gap in response["data"]["gaps"]:
        print(f"GAP {gap['code']}: {gap['message']}")


def _print_plan(envelope: dict[str, Any]) -> None:
    data = envelope["response"]["data"]
    print(f"decision_id: {data['decision_id']}")
    print(f"primary_type: {data['primary_type']}")
    print(f"gate: {data['gate']['decision']} ({data['gate']['reason_code']})")
    for step in data["route"]["steps"]:
        print(
            f"{step['seq']}. {step['operation']} -> {step['resource_ref']} "
            f"[{step['mode']}]"
        )


def main() -> int:
    """Run the gateway CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10, choices=range(1, 51))
    search_parser.add_argument("--json", action="store_true")
    search_parser.add_argument("--index", type=Path, default=INDEX_PATH)
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("goal")
    plan_parser.add_argument(
        "--intent",
        choices=("discover", "read", "write", "execute", "evaluate"),
        default="read",
    )
    plan_parser.add_argument(
        "--budget",
        choices=("none", "read_only", "bounded_write", "bounded_execute"),
        default="read_only",
    )
    plan_parser.add_argument("--json", action="store_true")
    plan_parser.add_argument("--index", type=Path, default=INDEX_PATH)
    invoke_parser = subparsers.add_parser("invoke")
    invoke_parser.add_argument("resource_ref")
    invoke_parser.add_argument("--decision-id", required=True)
    invoke_parser.add_argument("--operation", default="render_call")
    invoke_parser.add_argument("--json", action="store_true")
    invoke_parser.add_argument("--index", type=Path, default=INDEX_PATH)
    args = parser.parse_args()
    try:
        if args.command == "search":
            envelope = search(args.query, args.limit, index_path=args.index)
        elif args.command == "plan":
            envelope = plan(args.goal, args.intent, args.budget, index_path=args.index)
        else:
            envelope = invoke(
                args.index, args.resource_ref, args.decision_id, args.operation
            )
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    elif args.command == "search":
        _print_search(envelope)
    elif args.command == "plan":
        _print_plan(envelope)
    else:
        print(envelope["response"]["data"].get("command", "调用被拒绝"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


class TaskGateway:
    """Configured, dependency-free facade for the three gateway operations."""

    def __init__(self, index_path: Path | str | None = None) -> None:
        configured = index_path or os.environ.get("TASKGATEWAY_INDEX")
        self.index_path = Path(configured) if configured else INDEX_PATH

    def search(
        self,
        query: str,
        limit: int = 10,
        *,
        expand_hints: bool = True,
    ) -> dict[str, Any]:
        return search(
            query,
            limit,
            expand_hints=expand_hints,
            index_path=self.index_path,
        )

    def plan(
        self,
        goal: str,
        intent: str = "read",
        side_effect_budget: str = "read_only",
    ) -> dict[str, Any]:
        return plan(
            goal,
            intent,
            side_effect_budget,
            index_path=self.index_path,
        )

    def invoke(
        self,
        resource_ref: str,
        decision_id: str,
        operation: str = "render_call",
    ) -> dict[str, Any]:
        return invoke(self.index_path, resource_ref, decision_id, operation)

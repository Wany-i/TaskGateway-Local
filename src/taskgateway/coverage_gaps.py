"""Explicit unverified coverage-gap placeholders required by the contract."""

from __future__ import annotations

from typing import Any


UNVERIFIED_NOTE = (
    "UNVERIFIED 无实测证据（2026-09-16）—— 保留占位，不得据此宣称"
    "已覆盖该错误处理"
)


def detect(query: str, results: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return only mechanically observable placeholder gaps."""
    gaps: list[dict[str, str]] = []
    # UNVERIFIED 无实测证据（2026-09-16）—— 保留占位，不得据此宣称"已覆盖该错误处理"
    if any(item.get("summary_source") == "filename" for item in results):
        gaps.append(
            {"code": "TEXT_ONLY_INDEXED", "message": "候选资源仅有文件名级描述"}
        )
    # UNVERIFIED 无实测证据（2026-09-16）—— 保留占位，不得据此宣称"已覆盖该错误处理"
    if "文件" in query and any(item.get("type") == "library" for item in results):
        gaps.append(
            {"code": "LIBRARY_NOT_DRILLED", "message": "资料库仅索引到库级"}
        )
    # UNVERIFIED 无实测证据（2026-09-16）—— 保留占位，不得据此宣称"已覆盖该错误处理"
    platform_words = ("系统", "磁盘", "安装", "环境")
    known_platforms = ("windows", "c盘", "linux", "macos", "android", "ios")
    lowered = query.lower().replace(" ", "")
    if any(word in lowered for word in platform_words) and not any(
        platform in lowered for platform in known_platforms
    ):
        gaps.append({"code": "PLATFORM_UNKNOWN", "message": "任务未指明目标平台"})
    # UNVERIFIED 无实测证据（2026-09-16）—— 保留占位，不得据此宣称"已覆盖该错误处理"
    if len(results) > 1 and results[0].get("score") == results[1].get("score"):
        gaps.append({"code": "AMBIGUOUS", "message": "最高分候选并列"})
    return gaps

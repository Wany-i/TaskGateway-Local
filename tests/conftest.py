from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture()
def fixture_index(tmp_path: Path) -> Path:
    resource = tmp_path / "readme.md"
    resource.write_text("a local read-only resource\n", encoding="utf-8")
    payload = {
        "items": [
            {
                "ref": "tool://readme",
                "type": "tool",
                "name": "readme tool",
                "path": str(resource),
                "summary": "local read-only resource",
                "summary_source": "body",
                "keywords": ["readme", "resource", "local", "read-only"],
                "usage": f'Read "{resource}"',
                "disabled": False,
            },
            {
                "ref": "tool://disabled",
                "type": "tool",
                "name": "disabled tool",
                "path": str(resource),
                "summary": "disabled resource",
                "summary_source": "body",
                "keywords": ["disabled"],
                "usage": "never",
                "disabled": True,
            },
        ]
    }
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(payload), encoding="utf-8")
    return index_path

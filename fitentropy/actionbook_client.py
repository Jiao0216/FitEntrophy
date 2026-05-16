"""Actionbook CLI — optional action-manual hints for the LLM (no browser required)."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from typing import List

from fitentropy import config

logger = logging.getLogger(__name__)


def collect_retail_manual_hints() -> List[str]:
    """Run `actionbook search` for retailer / trend queries when CLI is on PATH."""

    if not config.ACTIONBOOK_CLI_HINTS:
        return []

    exe = shutil.which("actionbook")
    if not exe:
        logger.debug("actionbook CLI not found on PATH")
        return []

    queries = [
        "zara search products",
        "hm search shop",
        "uniqlo search",
    ]
    hints: List[str] = []
    for q in queries:
        for args in ((exe, "search", q, "--json"), (exe, "search", q)):
            try:
                proc = subprocess.run(
                    list(args),
                    capture_output=True,
                    text=True,
                    timeout=25,
                )
            except (subprocess.TimeoutExpired, OSError) as exc:
                logger.debug("actionbook search failed: %s", exc)
                break
            out = (proc.stdout or "").strip()
            if not out:
                continue
            try:
                parsed = json.loads(out)
                hints.append(json.dumps(parsed, ensure_ascii=False)[:1800])
            except json.JSONDecodeError:
                hints.append(out[:1800])
            break

    return hints

#!/usr/bin/env python3
"""Test LLM connectivity (OpenAI or Qwen per .env / LLM_PROVIDER)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy import config  # noqa: E402
from fitentropy.qwen_client import chat_completion_json  # noqa: E402


def main() -> int:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env_local = env_path.parent / ".env.local"
    print(f"Reading: {env_path} ({'exists' if env_path.exists() else 'MISSING'})")
    if env_local.exists():
        print(f"Also:   {env_local} (exists, overrides .env)")

    has_openai = bool(config.OPENAI_API_KEY)
    has_qwen = bool(config.QWEN_API_KEY)
    print(f"LLM_PROVIDER={config.LLM_PROVIDER!r}")
    print(f"  OPENAI_API_KEY: {'✓ set' if has_openai else '✗ empty'}")
    print(f"  QWEN_API_KEY:   {'✓ set' if has_qwen else '✗ empty'}")
    print(f"→ active: {config.llm_provider_label()} · model: {config.llm_model_label()}")
    if not config.llm_configured():
        print("ERROR: No API key for the active provider.", file=sys.stderr)
        if config.LLM_PROVIDER == "auto" and not has_openai and not has_qwen:
            print(
                "  .env 里 OPENAI_API_KEY= 和 QWEN_API_KEY= 仍是空的（未保存或写错文件）。\n"
                "  请编辑项目根目录 .env，同一行写：\n"
                "    OPENAI_API_KEY=sk-proj-你的密钥\n"
                "  保存后在本目录执行：\n"
                "    grep '^OPENAI_API_KEY=.' .env | wc -c   # 应 > 30\n"
                "  或临时： export OPENAI_API_KEY=sk-proj-...  再运行本脚本\n"
                "  获取：https://platform.openai.com/api-keys",
                file=sys.stderr,
            )
        elif config.active_llm_provider() == "openai":
            print("  请填写 OPENAI_API_KEY=sk-...（不要留空）", file=sys.stderr)
        else:
            print("  请填写 QWEN_API_KEY，或改 LLM_PROVIDER=auto 并设置 OPENAI_API_KEY", file=sys.stderr)
        return 1

    base, _key, model = config.llm_chat_config()
    print(f"Base URL: {base}")
    print("Calling chat/completions …")
    try:
        data = chat_completion_json(
            [
                {"role": "system", "content": "Reply with JSON only."},
                {
                    "role": "user",
                    "content": '{"ok": true, "provider": "test"}',
                },
            ],
            model=model,
            temperature=0,
            timeout=60,
        )
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    print("OK:", json.dumps(data, ensure_ascii=False)[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

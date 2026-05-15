from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List


def _load_history(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    if args.payload_json:
        payload = json.loads(args.payload_json)
        if not isinstance(payload, dict):
            raise ValueError("--payload-json must decode to a JSON object")
        payload.setdefault("ts", time.time())
        return payload

    return {
        "source": args.source,
        "message": args.message,
        "ts": time.time(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append one chat event to .pecs/ai_chat_history.json"
    )
    parser.add_argument("workspace_root", help="Workspace root path")
    parser.add_argument(
        "--source",
        default="manual",
        help="Chat source name (e.g. copilot, continue)",
    )
    parser.add_argument(
        "--message",
        default="",
        help="Simple message text for manual append mode",
    )
    parser.add_argument(
        "--payload-json",
        default="",
        help="Full JSON payload object string to append",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    pecs_dir = workspace_root / ".pecs"
    pecs_dir.mkdir(parents=True, exist_ok=True)

    chat_file = pecs_dir / "ai_chat_history.json"
    history = _load_history(chat_file)
    payload = _build_payload(args)
    history.append(payload)

    chat_file.write_text(
        json.dumps(history, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(f"Appended chat history to {chat_file}")


if __name__ == "__main__":
    main()

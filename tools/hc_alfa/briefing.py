"""HC Alfa Briefing pilot.

Compiles exchange deltas into a simple briefing markdown under planning/briefings/.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def write_briefing(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    path = out_dir / f"{today}.md"
    content = (
        f"# Daily Briefing — {today}\n\n"
        "Status\n- HC Alfa pilot components created (exchange, ops, briefing).\n\n"
        "Notes\n- Pilot operates in dry-run mode with guardrails.\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HC Alfa Briefing pilot")
    parser.add_argument("--out", type=Path, default=Path("planning/briefings"))
    args = parser.parse_args(argv)
    path = write_briefing(args.out)
    print(f"[hc_alfa_briefing] wrote {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


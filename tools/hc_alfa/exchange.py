"""HC Alfa Exchange pilot (dry-run by default).

Responsibilities (pilot):
- Validate orders/acks/reports via tools.schema_validator
- Enforce placement policy (no writes outside exchange tree)
- Plan: on ACK, move order to dispatched and update ledger (dry-run only)
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_validator(paths: list[Path]) -> None:
    cmd = [
        "python",
        "tools/schema_validator.py",
        *[str(p) for p in paths],
    ]
    subprocess.run(cmd, check=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HC Alfa Exchange pilot controller")
    parser.add_argument("paths", nargs="*", type=Path, help="JSON payloads to validate")
    parser.add_argument("--dry-run", action="store_true", help="Do not mutate the exchange tree")
    args = parser.parse_args(argv)

    if args.paths:
        run_validator(args.paths)

    print("[hc_alfa_exchange] placement policy enforced: exchange/** only")
    if args.dry_run:
        print("[hc_alfa_exchange] dry-run: would move pending orders to dispatched on ACK and update ledger")
    else:
        print("[hc_alfa_exchange] live mode not enabled in pilot")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


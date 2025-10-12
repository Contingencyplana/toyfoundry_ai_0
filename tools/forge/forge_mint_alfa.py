"""Toyfoundry Forge ritual script for minting a single Alfa prototype.

This ritual turns a recipe and set of parameters into a draft Alfa manifest.
It supports dry-run validation (default) and emits telemetry so the
manufacturing dashboards can track every invocation.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

TELEMETRY_DIR = Path(".toyfoundry") / "telemetry"
TELEMETRY_FILE = TELEMETRY_DIR / "forge_mint_alfa.jsonl"
DEFAULT_OUTPUT_DIR = Path("production") / "alfa_batches"


@dataclass
class AlfaManifest:
    alfa_id: str
    name: str
    seed: int
    created_at: str
    recipe_name: Optional[str] = None
    recipe: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "draft"

    def as_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        # Exclude empty keys for cleanliness
        return {key: value for key, value in payload.items() if value not in (None, {}, [])}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_recipe(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Recipe file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def compute_seed(explicit_seed: Optional[int]) -> int:
    if explicit_seed is not None:
        return explicit_seed
    random.seed()
    return random.randint(0, 2**31 - 1)


def build_manifest(name: str, recipe: Dict[str, Any], seed: Optional[int], extra_parameters: Dict[str, Any]) -> AlfaManifest:
    manifesto_seed = compute_seed(seed)
    alfa_id = f"alfa-{int(time.time())}-{manifesto_seed:08x}"
    recipe_name = recipe.get("name") if recipe else None
    parameters = recipe.get("parameters", {}).copy()
    parameters.update(extra_parameters)
    return AlfaManifest(
        alfa_id=alfa_id,
        name=name,
        seed=manifesto_seed,
        created_at=timestamp(),
        recipe_name=recipe_name,
        recipe=recipe,
        parameters=parameters,
    )


def write_manifest(manifest: AlfaManifest, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{manifest.alfa_id}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def emit_telemetry(manifest: AlfaManifest, output_path: Optional[Path], dry_run: bool) -> None:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": timestamp(),
        "alfa_id": manifest.alfa_id,
        "name": manifest.name,
        "dry_run": dry_run,
        "output_path": str(output_path) if output_path else None,
        "seed": manifest.seed,
        "recipe_name": manifest.recipe_name,
        "status": manifest.status,
    }
    with TELEMETRY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry))
        handle.write("\n")


def parse_extra_parameters(values: Optional[list[str]]) -> Dict[str, Any]:
    if not values:
        return {}
    parameters: Dict[str, Any] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid parameter specification (expected key=value): {item}")
        key, value = item.split("=", 1)
        parameters[key] = value
    return parameters


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mint an Alfa manifest using Toyfoundry Forge rituals.")
    parser.add_argument("--name", required=True, help="Display name for the Alfa prototype.")
    parser.add_argument("--recipe", type=Path, help="Path to a recipe JSON file.")
    parser.add_argument("--seed", type=int, help="Optional deterministic seed.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory where manifests are written (ignored with --dry-run).")
    parser.add_argument("--param", action="append", help="Override or extend parameters, e.g. --param color=azure --param tempo=allegro.")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing the manifest to disk.")
    parser.add_argument("--quiet", action="store_true", help="Suppress human-friendly output (telemetry is still written).")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    try:
        args = parse_args(argv)
        recipe = load_recipe(args.recipe)
        extra_parameters = parse_extra_parameters(args.param)
        manifest = build_manifest(args.name, recipe, args.seed, extra_parameters)
        output_path: Optional[Path] = None
        if not args.dry_run:
            output_path = write_manifest(manifest, args.output_dir)
            manifest.status = "minted"
        emit_telemetry(manifest, output_path, args.dry_run)
        if not args.quiet:
            print(f"Minted Alfa {manifest.alfa_id} (dry_run={args.dry_run})")
            if output_path:
                print(f"Manifest written to {output_path}")
            else:
                print("Manifest not written (dry run). Telemetry recorded.")
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print(f"forge_mint_alfa failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
generate_build_info.py — Generate build_info.json and checksums for export batches
"""

import json
import hashlib
import datetime
import sys
from pathlib import Path


def generate_build_info(export_dir: Path, order_id: str, batch_name: str, batch_count: int):
    """Generate build_info.json with SHA256 checksums."""
    
    # Collect artifacts
    artifacts = {}
    for artifact_file in export_dir.glob("composite_export.*"):
        if artifact_file.is_file():
            sha256_hash = hashlib.sha256(artifact_file.read_bytes()).hexdigest()
            artifacts[artifact_file.name] = sha256_hash
            
            # Write individual .sha256 file
            sha256_file = export_dir / f"{artifact_file.name}.sha256"
            sha256_file.write_text(f"{sha256_hash}  {artifact_file.name}\n")
    
    # Build metadata
    build_info = {
        "order_id": order_id,
        "batch_name": batch_name,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "artifacts": artifacts,
        "batch_count": batch_count,
        "retention_days": 7,
        "rollback_plan": "Revert to previous export; purge canary Alfas if entropy >0.7"
    }
    
    # Write build_info.json
    build_info_path = export_dir / "build_info.json"
    build_info_path.write_text(json.dumps(build_info, indent=2))
    print(f"✅ Build info written to {build_info_path}")
    
    # Write export_manifest.json
    manifest = {
        "files": list(artifacts.keys()),
        "checksums": artifacts
    }
    manifest_path = export_dir / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"✅ Export manifest written to {manifest_path}")
    
    return build_info


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: generate_build_info.py <export_dir> <order_id> <batch_name> <batch_count>")
        sys.exit(1)
    
    export_dir = Path(sys.argv[1])
    order_id = sys.argv[2]
    batch_name = sys.argv[3]
    batch_count = int(sys.argv[4])
    
    generate_build_info(export_dir, order_id, batch_name, batch_count)

#!/usr/bin/env python3
"""
mission_controller.py — Order Execution Logic and Victory Conditions
Tracks High Command orders, validates completion criteria, and generates reports.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# Order definitions with victory conditions
ACTIVE_ORDERS = {
    "order-2025-10-15-020": {
        "summary": "Standard batch run with limits",
        "priority": "high",
        "expires": "2025-10-19T00:00:00Z",
        "victory_conditions": [
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/composite_export.json",
                "description": "Composite export JSON generated"
            },
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/composite_export.csv",
                "description": "Composite export CSV generated"
            },
            {
                "type": "forge_execution",
                "ritual": "mint",
                "param": "batch",
                "value": 8,
                "description": "Minted batch with max_alfa_per_batch=8"
            }
        ],
        "directives": [
            "Configure batch_limits (max_alfa_per_batch=8)",
            "Execute standard run with telemetry",
            "Emit composite exports with checksums",
            "Publish artifact locations",
            "Submit completion report"
        ]
    },
    "order-2025-10-15-024": {
        "summary": "Daylands safety pipeline pilot",
        "priority": "normal",
        "expires": "2025-10-22T00:00:00Z",
        "victory_conditions": [
            {
                "type": "docs_updated",
                "paths": ["planning/daylands_and_nightlands.md"],
                "description": "Daylands charter documented"
            },
            {
                "type": "sandbox_validated",
                "description": "Templates and lanes config validated"
            }
        ],
        "directives": [
            "Propose Daylands charter + safety checklist",
            "Sandbox validation (docs-only)",
            "Canary rollout simulation",
            "Submit pipeline status report"
        ]
    },
    "order-2025-10-15-026": {
        "summary": "Pivotal fronts pointer",
        "priority": "standard",
        "expires": "2025-10-22T00:00:00Z",
        "status": "COMPLETED",
        "victory_conditions": [
            {
                "type": "artifact_exists",
                "path": "planning/pivotal_fronts_pointer.md",
                "description": "Pointer document created",
                "satisfied": True
            }
        ],
        "completion_notes": "Created pivotal_fronts_pointer.md linking to High Command canon"
    },
    "order-2025-10-15-028": {
        "summary": "Canary Alfa batches with exports",
        "priority": "high",
        "expires": "2025-10-22T00:00:00Z",
        "dependencies": ["order-2025-10-15-024"],
        "victory_conditions": [
            {
                "type": "forge_execution",
                "ritual": "mint",
                "count": 3,
                "description": "Minted 2-3 canary batches"
            },
            {
                "type": "artifacts_exist",
                "paths": [
                    ".toyfoundry/telemetry/quilt/exports/composite_export.json",
                    ".toyfoundry/telemetry/quilt/exports/composite_export.csv"
                ],
                "description": "Canary exports generated"
            },
            {
                "type": "checksum_files",
                "pattern": "*.sha256",
                "description": "SHA256 checksums generated"
            }
        ],
        "directives": [
            "Propose change with Order 025 metadata",
            "Sandbox validation with dry-run",
            "Mint 2-3 canary batches with telemetry",
            "Submit report with paths/counts/checksums"
        ]
    },
    "order-2025-10-15-030": {
        "summary": "Expand canary with 2 additional batches",
        "priority": "high",
        "expires": "2025-10-23T00:00:00Z",
        "dependencies": ["order-2025-10-15-028"],
        "victory_conditions": [
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/canary_batch_b1.json",
                "description": "Canary batch B1 generated"
            },
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/canary_batch_b1.csv",
                "description": "Canary batch B1 CSV generated"
            },
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/canary_batch_b2.json",
                "description": "Canary batch B2 generated"
            },
            {
                "type": "artifact_exists",
                "path": ".toyfoundry/telemetry/quilt/exports/canary_batch_b2.csv",
                "description": "Canary batch B2 CSV generated"
            }
        ],
        "directives": [
            "Propose change with Order 025 metadata",
            "Emit canary_batch_b1.csv/json",
            "Emit canary_batch_b2.csv/json",
            "Submit report with per-batch details"
        ]
    }
}


class MissionController:
    """Tracks order execution progress and validates victory conditions."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.orders = ACTIVE_ORDERS.copy()
    
    def check_victory_conditions(self, order_id: str) -> Dict:
        """
        Check if all victory conditions for an order are satisfied.
        Returns dict with satisfied count, total count, and details.
        """
        if order_id not in self.orders:
            return {"error": f"Unknown order: {order_id}"}
        
        order = self.orders[order_id]
        
        if order.get("status") == "COMPLETED":
            return {
                "order_id": order_id,
                "status": "COMPLETED",
                "satisfied": len(order["victory_conditions"]),
                "total": len(order["victory_conditions"]),
                "complete": True
            }
        
        conditions = order.get("victory_conditions", [])
        results = []
        satisfied_count = 0
        
        for condition in conditions:
            result = self._check_condition(condition)
            results.append(result)
            if result["satisfied"]:
                satisfied_count += 1
        
        return {
            "order_id": order_id,
            "satisfied": satisfied_count,
            "total": len(conditions),
            "complete": satisfied_count == len(conditions),
            "conditions": results
        }
    
    def _check_condition(self, condition: Dict) -> Dict:
        """Check a single victory condition."""
        ctype = condition.get("type")
        
        if ctype == "artifact_exists":
            path = self.workspace_root / condition["path"]
            satisfied = path.exists()
            return {
                "description": condition["description"],
                "satisfied": satisfied,
                "details": f"File {'found' if satisfied else 'missing'}: {condition['path']}"
            }
        
        elif ctype == "artifacts_exist":
            paths = condition.get("paths", [])
            all_exist = all((self.workspace_root / p).exists() for p in paths)
            return {
                "description": condition["description"],
                "satisfied": all_exist,
                "details": f"All files {'present' if all_exist else 'missing'}"
            }
        
        elif ctype == "forge_execution":
            # Check telemetry logs for forge execution
            ritual = condition.get("ritual")
            return {
                "description": condition["description"],
                "satisfied": False,  # Requires telemetry parsing (TODO)
                "details": f"Forge {ritual} execution check pending"
            }
        
        elif ctype in ["docs_updated", "sandbox_validated", "checksum_files"]:
            return {
                "description": condition["description"],
                "satisfied": False,  # Manual verification required
                "details": f"{ctype} check requires manual verification"
            }
        
        else:
            return {
                "description": condition.get("description", "Unknown condition"),
                "satisfied": False,
                "details": f"Unknown condition type: {ctype}"
            }
    
    def get_mission_status(self) -> Dict:
        """Get overall mission status for all active orders."""
        status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "orders": {}
        }
        
        for order_id, order_data in self.orders.items():
            check_result = self.check_victory_conditions(order_id)
            
            status["orders"][order_id] = {
                "summary": order_data["summary"],
                "priority": order_data["priority"],
                "expires": order_data["expires"],
                "status": order_data.get("status", "IN_PROGRESS"),
                "victory": check_result
            }
        
        return status
    
    def display_mission_briefing(self):
        """Print formatted mission briefing with order status."""
        print("\n" + "="*70)
        print("📜 MISSION BRIEFING — Active High Command Orders")
        print("="*70)
        
        for order_id, order_data in sorted(self.orders.items()):
            status = order_data.get("status", "IN_PROGRESS")
            emoji = "✅" if status == "COMPLETED" else "⏳"
            
            print(f"\n{emoji} {order_id}")
            print(f"   Summary: {order_data['summary']}")
            print(f"   Priority: {order_data['priority']}")
            print(f"   Expires: {order_data['expires']}")
            
            if status == "COMPLETED":
                print(f"   Status: {status} ✅")
                if "completion_notes" in order_data:
                    print(f"   Notes: {order_data['completion_notes']}")
            else:
                check = self.check_victory_conditions(order_id)
                print(f"   Progress: {check['satisfied']}/{check['total']} conditions met")
                
                if "conditions" in check:
                    for cond in check["conditions"]:
                        icon = "✅" if cond["satisfied"] else "❌"
                        print(f"      {icon} {cond['description']}")
        
        print("\n" + "="*70)


def main():
    """Standalone mission controller for checking order status."""
    workspace_root = Path(__file__).parent.parent.parent.parent
    controller = MissionController(workspace_root)
    
    controller.display_mission_briefing()
    
    # Export full status to JSON
    status = controller.get_mission_status()
    status_file = Path("mission_status.json")
    
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)
    
    print(f"\n💾 Full mission status exported to: {status_file}")


if __name__ == "__main__":
    main()

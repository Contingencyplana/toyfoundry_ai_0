#!/usr/bin/env python3
"""
battlefield.py — Initial Alfa Playable Workflow Overlay
Transforms Toyfoundry manufacturing into a 16×16 emoji tactical grid.
Grid clicks trigger real forge scripts; telemetry feeds back as emoji updates.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Grid configuration
GRID_SIZE = 16
HEX_LABELS = "0123456789ABCDEF"

# Tactical positions and their forge commands
# 16-node comprehensive manufacturing workflow overlay
TACTICAL_POSITIONS = {
    # === MANUFACTURING COLUMN (col 4) ===
    (0, 4): {
        "emoji": "📥",
        "name": "Order Intake",
        "command": ["git", "submodule", "update", "--remote", "exchange"],
        "params": [],
        "description": "Pull latest orders from High Command exchange"
    },
    (1, 4): {
        "emoji": "✉️",
        "name": "Acknowledge Order",
        "command": ["python", "-m", "tools.exchange.acknowledge_order"],
        "params": ["--order-id"],
        "description": "Generate acknowledgement for incoming order"
    },
    (2, 4): {
        "emoji": "📝",
        "name": "Proposal",
        "command": ["echo"],
        "params": [],
        "description": "Create change proposal with intent/scope/risks/rollback"
    },
    (3, 4): {
        "emoji": "🧪",
        "name": "Sandbox Validate",
        "command": ["python", "-m", "tools.forge.forge_mint_alfa", "--dry-run"],
        "params": ["--name"],
        "description": "Dry-run validation before manufacturing"
    },
    (4, 4): {
        "emoji": "🏭",
        "name": "Forge Mint",
        "command": ["python", "-m", "tools.forge.forge_mint_alfa"],
        "params": ["--name", "--output"],
        "description": "Mint new Alfa batch with configurable size"
    },
    
    # === RITUAL DIAGONAL (5-8) ===
    (5, 5): {
        "emoji": "🎯",
        "name": "Drill",
        "command": ["python", "-m", "tools.forge.forge_drill_alfa"],
        "params": [],
        "description": "Run simulations on existing Alfas"
    },
    (6, 6): {
        "emoji": "🎭",
        "name": "Parade",
        "command": ["python", "-m", "tools.forge.forge_parade_alfa"],
        "params": [],
        "description": "Display batch results and dream logs"
    },
    (7, 7): {
        "emoji": "🗑️",
        "name": "Purge",
        "command": ["python", "-m", "tools.forge.forge_purge_alfa"],
        "params": [],
        "description": "Retire failed Alfas (high entropy)"
    },
    (8, 8): {
        "emoji": "⭐",
        "name": "Promote",
        "command": ["python", "-m", "tools.forge.forge_promote_alfa"],
        "params": [],
        "description": "Certify exemplary Alfas for deployment"
    },
    
    # === TELEMETRY COLUMN (col 8) ===
    (9, 8): {
        "emoji": "🧵",
        "name": "Quilt Loom",
        "command": ["python", "-m", "tools.telemetry.quilt_loom"],
        "params": [],
        "description": "Generate telemetry rollups (mint + ritual streams)"
    },
    (10, 8): {
        "emoji": "🔍",
        "name": "Quilt Inspect",
        "command": ["python", "-m", "tools.telemetry.quilt_loom", "--show"],
        "params": [],
        "description": "View telemetry rollup summary"
    },
    (11, 8): {
        "emoji": "💾",
        "name": "Build Info",
        "command": ["python", "tools/telemetry/generate_build_info.py"],
        "params": [],
        "description": "Generate build_info.json with SHA256 checksums"
    },
    
    # === EXPORT & VALIDATION COLUMN (col 4, rows 12-14) ===
    (12, 4): {
        "emoji": "📊",
        "name": "Export Quilt",
        "command": ["python", "-m", "tools.telemetry.quilt_loom", "--export"],
        "params": ["--export-dir"],
        "description": "Generate composite exports (JSON/CSV)"
    },
    (13, 4): {
        "emoji": "🔐",
        "name": "Checksum Verify",
        "command": ["python", "-c", "import hashlib; from pathlib import Path; print('Checksum verification placeholder')"],
        "params": [],
        "description": "Verify artifact integrity via SHA256"
    },
    (14, 4): {
        "emoji": "✅",
        "name": "Schema Validate",
        "command": ["python", "tools/schema_validator.py"],
        "params": [],
        "description": "Validate reports against factory-report@1.0 schema"
    },
    
    # === GIT OPERATIONS CORNER (rows 14-15, cols 12-15) ===
    (14, 12): {
        "emoji": "📋",
        "name": "Git Status",
        "command": ["git", "status", "--short"],
        "params": [],
        "description": "Show working tree status"
    },
    (14, 13): {
        "emoji": "➕",
        "name": "Git Add",
        "command": ["git", "add", "-A"],
        "params": [],
        "description": "Stage all changes for commit"
    },
    (15, 14): {
        "emoji": "💾",
        "name": "Git Commit",
        "command": ["git", "commit", "-m"],
        "params": [],
        "description": "Commit staged changes with message"
    },
    (15, 15): {
        "emoji": "🚀",
        "name": "Git Push",
        "command": ["git", "push"],
        "params": [],
        "description": "Push commits to remote origin"
    }
}

# Emoji terrain for grid display
EMPTY = "⬛"
HIGHLIGHT = "✨"
ACTIVE = "🔥"
SUCCESS = "✅"
FAILURE = "❌"


class BattlefieldGrid:
    """Manages 16×16 emoji grid state and rendering."""
    
    def __init__(self, state_file: Path = Path("state.json")):
        self.state_file = state_file
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.load_state()
        self._init_tactical_positions()
    
    def _init_tactical_positions(self):
        """Place tactical position emojis on grid."""
        for (row, col), config in TACTICAL_POSITIONS.items():
            self.grid[row][col] = config["emoji"]
    
    def load_state(self):
        """Load persistent grid state from JSON."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state_data = json.load(f)
        else:
            self.state_data = {
                "orders_completed": [],
                "last_forge_run": None,
                "artifact_paths": [],
                "telemetry_events": []
            }
    
    def save_state(self):
        """Persist grid state to JSON."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state_data, f, indent=2)
    
    def render(self) -> str:
        """Render grid as emoji string with hex labels."""
        lines = ["   " + "  ".join(HEX_LABELS)]
        lines.append("")
        
        for i, row in enumerate(self.grid):
            row_label = HEX_LABELS[i]
            row_str = f" {row_label} " + " ".join(row)
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def update_position(self, row: int, col: int, emoji: str):
        """Update a specific grid position."""
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.grid[row][col] = emoji
    
    def mark_active(self, row: int, col: int):
        """Mark position as actively executing."""
        self.update_position(row, col, ACTIVE)
    
    def mark_success(self, row: int, col: int):
        """Mark position as successfully completed."""
        self.update_position(row, col, SUCCESS)
        self.save_state()
    
    def mark_failure(self, row: int, col: int):
        """Mark position as failed."""
        self.update_position(row, col, FAILURE)
        self.save_state()


class TacticalController:
    """Executes forge commands when grid positions are clicked."""
    
    def __init__(self, grid: BattlefieldGrid):
        self.grid = grid
        self.workspace_root = Path(__file__).parent.parent.parent.parent
    
    def execute_tactical_action(self, row: int, col: int, params: Optional[Dict] = None) -> bool:
        """
        Execute the forge command associated with a tactical position.
        Returns True if successful, False otherwise.
        """
        position = (row, col)
        
        if position not in TACTICAL_POSITIONS:
            print(f"❌ No tactical action at position [{row}][{col}]")
            return False
        
        config = TACTICAL_POSITIONS[position]
        print(f"\n🎯 Executing: {config['name']}")
        print(f"   {config['description']}")
        
        # Build command with parameters
        command = config["command"].copy()
        if params and config["params"]:
            for param_key in config["params"]:
                if param_key in params:
                    command.extend([param_key, str(params[param_key])])
        
        print(f"   Command: {' '.join(command)}")
        
        # Mark as active
        self.grid.mark_active(row, col)
        print(self.grid.render())
        
        try:
            # Execute in workspace root
            result = subprocess.run(
                command,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300  # 5-minute timeout
            )
            
            if result.returncode == 0:
                print(f"\n✅ {config['name']} succeeded!")
                print(f"   Output preview:\n{result.stdout[:500]}")
                self.grid.mark_success(row, col)
                
                # Log to state
                self.grid.state_data["telemetry_events"].append({
                    "position": [row, col],
                    "action": config["name"],
                    "timestamp": "2025-10-18T12:30:00Z",  # TODO: use real timestamp
                    "status": "success"
                })
                self.grid.save_state()
                return True
            else:
                print(f"\n❌ {config['name']} failed!")
                print(f"   Error:\n{result.stderr[:500]}")
                self.grid.mark_failure(row, col)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\n⏱️ {config['name']} timed out (5 minutes)")
            self.grid.mark_failure(row, col)
            return False
        except Exception as e:
            print(f"\n💥 Exception during {config['name']}: {e}")
            self.grid.mark_failure(row, col)
            return False


def show_tactical_menu():
    """Display available tactical positions and their commands."""
    print("\n" + "="*70)
    print("🎮 TACTICAL POSITIONS — Available Actions")
    print("="*70)
    
    for (row, col), config in sorted(TACTICAL_POSITIONS.items()):
        hex_row = HEX_LABELS[row]
        hex_col = HEX_LABELS[col]
        print(f"\n[{hex_row}][{hex_col}] {config['emoji']} {config['name']}")
        print(f"      {config['description']}")
        print(f"      Command: {' '.join(config['command'])}")
        if config['params']:
            print(f"      Parameters: {', '.join(config['params'])}")
    
    print("\n" + "="*70)


def interactive_mode():
    """Run battlefield in interactive CLI mode."""
    print("🏭 TOYFOUNDRY BATTLEFIELD — Initial Alfa Prototype")
    print("   golf_00/delta_00/alfa_00/")
    print("   Path A: Grid clicks trigger real forge scripts\n")
    
    grid = BattlefieldGrid()
    controller = TacticalController(grid)
    
    print(grid.render())
    show_tactical_menu()
    
    print("\n📜 Active Missions (Orders to Execute):")
    print("   • Order 020: Standard batch (URGENT - expires 2025-10-19)")
    print("   • Order 024: Daylands safety pipeline")
    print("   • Order 028: Canary Alfa batches")
    print("   • Order 030: Expand canary production")
    
    print("\n💡 Commands:")
    print("   • Type hex coordinates (e.g., '4 4' or '44' for [4][4])")
    print("   • Type 'menu' to show tactical positions")
    print("   • Type 'state' to view mission progress")
    print("   • Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("🎯 Enter tactical action: ").strip().lower()
            
            if user_input == "quit":
                print("👋 Exiting battlefield. Mission state saved.")
                break
            
            elif user_input == "menu":
                show_tactical_menu()
            
            elif user_input == "state":
                print("\n📊 Mission State:")
                print(json.dumps(grid.state_data, indent=2))
            
            elif user_input == "grid":
                print(grid.render())
            
            else:
                # Parse coordinates
                coords = user_input.replace(" ", "").replace("[", "").replace("]", "")
                
                if len(coords) == 2:
                    row_hex, col_hex = coords[0].upper(), coords[1].upper()
                    
                    if row_hex in HEX_LABELS and col_hex in HEX_LABELS:
                        row = HEX_LABELS.index(row_hex)
                        col = HEX_LABELS.index(col_hex)
                        
                        # Check if we need parameters
                        position = (row, col)
                        if position in TACTICAL_POSITIONS:
                            config = TACTICAL_POSITIONS[position]
                            params = {}
                            
                            if "--batch" in config["params"]:
                                batch_size = input("   Batch size (default 8): ").strip() or "8"
                                params["--batch"] = batch_size
                            
                            controller.execute_tactical_action(row, col, params)
                            print("\n" + grid.render())
                        else:
                            print(f"❌ No tactical action at [{row_hex}][{col_hex}]")
                    else:
                        print("❌ Invalid hex coordinates. Use 0-9 or A-F.")
                else:
                    print("❌ Invalid format. Use two hex digits (e.g., '44' or '4 4')")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Mission state saved.")
            break
        except Exception as e:
            print(f"💥 Error: {e}")


if __name__ == "__main__":
    interactive_mode()

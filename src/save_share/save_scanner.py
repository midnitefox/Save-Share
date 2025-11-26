import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from .rom_index import RomRecord

SAVE_EXTENSIONS = {".sav", ".srm", ".mcr", ".eep", ".fla", ".rmc"}
STATE_EXTENSIONS = {".state", ".state1", ".state2", ".state3", ".0", ".1", ".2", ".3"}


@dataclass
class SaveRecord:
    system: str
    save_type: str  # "sram" or "state"
    rom_hash: str
    rom_name: str
    path: str
    slot: Optional[int] = None
    core: Optional[str] = None


class SaveScanner:
    def __init__(self, saves_root: str):
        self.saves_root = saves_root

    def _detect_slot(self, filename: str) -> Optional[int]:
        match = re.search(r"(state|\.)(\d)$", filename)
        if match:
            return int(match.group(2))
        return None

    def scan(self, rom_index: List[RomRecord]) -> List[SaveRecord]:
        lookup_by_system: Dict[str, Dict[str, RomRecord]] = {}
        for rom in rom_index:
            lookup_by_system.setdefault(rom.system, {})[os.path.basename(rom.rom_path)] = rom

        saves: List[SaveRecord] = []
        for system, roms in lookup_by_system.items():
            system_save_path = os.path.join(self.saves_root, system)
            if not os.path.isdir(system_save_path):
                continue
            for root, _, files in os.walk(system_save_path):
                for fname in files:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in SAVE_EXTENSIONS and ext not in STATE_EXTENSIONS:
                        continue
                    save_type = "sram" if ext in SAVE_EXTENSIONS else "state"
                    slot = self._detect_slot(fname) if save_type == "state" else None
                    rom_name = os.path.splitext(fname)[0]
                    rom_record = roms.get(f"{rom_name}{ext}") or roms.get(f"{rom_name}")
                    if not rom_record:
                        # try matching with any ext by rom base name
                        rom_record = next((r for r in roms.values() if os.path.splitext(os.path.basename(r.rom_path))[0] == rom_name), None)
                    if not rom_record:
                        continue
                    saves.append(
                        SaveRecord(
                            system=system,
                            save_type=save_type,
                            rom_hash=rom_record.rom_hash,
                            rom_name=rom_record.title,
                            path=os.path.join(root, fname),
                            slot=slot,
                        )
                    )
        return saves


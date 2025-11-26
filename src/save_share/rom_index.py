import hashlib
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional

from .gamelist import GameEntry


@dataclass
class RomRecord:
    system: str
    title: str
    rom_path: str
    rom_hash: str


class RomIndex:
    def __init__(self, cache_path: Optional[str] = None):
        self.cache_path = cache_path
        self.records: List[RomRecord] = []

    def load_cache(self) -> None:
        if self.cache_path and os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.records = [RomRecord(**row) for row in data.get("roms", [])]

    def save_cache(self) -> None:
        if not self.cache_path:
            return
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump({"roms": [asdict(r) for r in self.records]}, f, indent=2)

    def compute_hash(self, rom_full_path: str) -> str:
        md5 = hashlib.md5()
        with open(rom_full_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def index_games(self, roms_root: str, game_entries: Iterable[GameEntry]) -> List[RomRecord]:
        indexed: List[RomRecord] = []
        for entry in game_entries:
            rom_full_path = entry.rom_path
            if not os.path.isabs(rom_full_path):
                rom_full_path = os.path.join(roms_root, entry.system, rom_full_path)
            if not os.path.exists(rom_full_path):
                continue
            rom_hash = self.compute_hash(rom_full_path)
            indexed.append(
                RomRecord(
                    system=entry.system,
                    title=entry.title,
                    rom_path=os.path.abspath(rom_full_path),
                    rom_hash=rom_hash,
                )
            )
        self.records = indexed
        return indexed

    def by_system(self) -> Dict[str, List[RomRecord]]:
        systems: Dict[str, List[RomRecord]] = {}
        for record in self.records:
            systems.setdefault(record.system, []).append(record)
        return systems

    def as_lookup(self) -> Dict[str, RomRecord]:
        return {f"{r.system}:{os.path.basename(r.rom_path)}": r for r in self.records}


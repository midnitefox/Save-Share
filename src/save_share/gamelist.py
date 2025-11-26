import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class GameEntry:
    system: str
    title: str
    rom_path: str


def parse_gamelist(gamelist_path: str, system: str) -> List[GameEntry]:
    if not os.path.exists(gamelist_path):
        return []
    tree = ET.parse(gamelist_path)
    root = tree.getroot()
    games: List[GameEntry] = []
    for game in root.findall("game"):
        path_el = game.find("path")
        name_el = game.find("name")
        if path_el is None or name_el is None:
            continue
        rom_path = path_el.text or ""
        title = name_el.text or os.path.basename(rom_path)
        games.append(GameEntry(system=system, title=title.strip(), rom_path=rom_path.strip()))
    return games


def collect_all_gamelists(roms_root: str) -> Iterable[GameEntry]:
    for system in sorted(os.listdir(roms_root)):
        system_path = os.path.join(roms_root, system)
        if not os.path.isdir(system_path):
            continue
        gamelist_path = os.path.join(system_path, "gamelist.xml")
        for game in parse_gamelist(gamelist_path, system):
            yield game


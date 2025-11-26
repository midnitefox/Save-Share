import os
from typing import List

from .rom_index import RomRecord
from .save_scanner import SaveRecord
from .supabase_client import RemoteSave, SupabaseClient


def print_header(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)


def prompt_choice(options: List[str], allow_back: bool = True) -> int:
    for idx, opt in enumerate(options, 1):
        print(f"[{idx}] {opt}")
    if allow_back:
        print("[0] Back/Cancel")
    choice = input("Select: ")
    try:
        value = int(choice)
        if 0 <= value <= len(options):
            return value
    except ValueError:
        pass
    return -1


def choose_save_to_upload(saves: List[SaveRecord]) -> SaveRecord:
    print_header("Pick a save/state to upload")
    options = [f"{s.system} | {s.rom_name} | {s.save_type} | {os.path.basename(s.path)}" for s in saves]
    idx = prompt_choice(options)
    if idx <= 0:
        raise SystemExit("Cancelled")
    return saves[idx - 1]


def collect_tags() -> List[str]:
    presets = ["Boss", "100%", "All items", "Early", "Mid", "Late"]
    print("Tag presets (toggle by number, blank to continue):")
    selected: List[str] = []
    while True:
        for i, tag in enumerate(presets, 1):
            marker = "x" if tag in selected else " "
            print(f"[{i}] [{marker}] {tag}")
        raw = input("Toggle number or Enter when done: ").strip()
        if raw == "":
            break
        try:
            idx = int(raw)
            if 1 <= idx <= len(presets):
                tag = presets[idx - 1]
                if tag in selected:
                    selected.remove(tag)
                else:
                    selected.append(tag)
        except ValueError:
            continue
    extra = input("Extra tags (comma separated, optional): ").strip()
    if extra:
        selected.extend([t.strip() for t in extra.split(",") if t.strip()])
    return selected


def list_remote(supabase: SupabaseClient, local_roms: List[RomRecord]) -> None:
    filters = [{"system": r.system, "rom_hash": r.rom_hash} for r in local_roms]
    remote = supabase.list_remote_saves(filters)
    if not remote:
        print("No remote saves for your library yet.")
        return
    by_system: dict = {}
    for save in remote:
        by_system.setdefault(save.system, []).append(save)
    for system, saves in by_system.items():
        print_header(system)
        by_game: dict = {}
        for s in saves:
            by_game.setdefault(s.rom_hash, []).append(s)
        for rom_hash, entries in by_game.items():
            title = entries[0].rom_name
            print(f"- {title} ({rom_hash})")
            for entry in entries:
                tags = ", ".join(entry.tags)
                core_label = f" [{entry.core}]" if entry.core else ""
                print(f"   * {entry.save_type}{core_label} by {entry.uploader}: {entry.description} | {tags}")


def download_flow(supabase: SupabaseClient, local_roms: List[RomRecord], dest_root: str) -> None:
    remote = supabase.list_remote_saves([
        {"system": r.system, "rom_hash": r.rom_hash} for r in local_roms
    ])
    if not remote:
        print("No remote saves available to download.")
        return
    options = [f"{r.system} | {r.rom_name} | {r.save_type} | core={r.core}" for r in remote]
    idx = prompt_choice(options)
    if idx <= 0:
        return
    selection = remote[idx - 1]
    data = supabase.download_save("saves", selection.storage_path)
    if data is None:
        print("Failed to download from Supabase. Check network and credentials.")
        return
    system_path = os.path.join(dest_root, selection.system)
    os.makedirs(system_path, exist_ok=True)
    filename = f"{selection.rom_name}.{selection.save_type}"
    target = os.path.join(system_path, filename)
    with open(target, "wb") as f:
        f.write(data)
    print(f"Saved to {target}")


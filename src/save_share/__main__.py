import argparse
import os
import sys
import uuid

from .config import Config
from .gamelist import collect_all_gamelists
from .rom_index import RomIndex
from .save_scanner import SaveScanner
from .supabase_client import SupabaseClient
from .ui_cli import choose_save_to_upload, collect_tags, download_flow, list_remote


def build_index(config: Config) -> RomIndex:
    index = RomIndex(cache_path=config.cache_path)
    index.load_cache()
    games = list(collect_all_gamelists(config.roms_path))
    indexed = index.index_games(config.roms_path, games)
    index.save_cache()
    print(f"Indexed {len(indexed)} ROMs")
    return index


def scan_saves(config: Config, rom_index: RomIndex):
    scanner = SaveScanner(config.saves_path)
    saves = scanner.scan(rom_index.records)
    print(f"Detected {len(saves)} saves/states")
    for s in saves:
        print(f"{s.system} | {s.rom_name} | {s.save_type} | {s.path}")
    return saves


def upload_flow(config: Config, rom_index: RomIndex):
    saves = scan_saves(config, rom_index)
    if not saves:
        print("No saves found")
        return
    save = choose_save_to_upload(saves)
    core = None
    if save.save_type == "state":
        core = input("Enter core used for this savestate (e.g., snes9x, pcsx_rearmed): ").strip() or None
    description = input("Describe this save/state: ")
    tags = collect_tags()
    supabase = SupabaseClient(config.supabase_url, config.supabase_key)
    game_id = supabase.upsert_game(save.system, save.rom_hash, save.rom_name)
    if not game_id:
        print("Failed to upsert game")
        return
    save_uuid = str(uuid.uuid4())
    storage_path = f"{save.system}/{save.rom_hash}/{save_uuid}.bin"
    save_id = supabase.upload_save_metadata(
        game_id,
        save.save_type,
        core,
        tags,
        description,
        config.device_nickname,
        storage_path,
        save_uuid,
    )
    if not save_id:
        print("Failed to create save entry")
        return
    with open(save.path, "rb") as f:
        data = f.read()
    ok = supabase.upload_binary("saves", storage_path, data)
    if ok:
        print("Upload complete!")
    else:
        print("Failed to upload binary to storage")


def browse_flow(config: Config, rom_index: RomIndex):
    supabase = SupabaseClient(config.supabase_url, config.supabase_key)
    list_remote(supabase, rom_index.records)


def download_cli(config: Config, rom_index: RomIndex):
    supabase = SupabaseClient(config.supabase_url, config.supabase_key)
    download_flow(supabase, rom_index.records, config.saves_path)


def main():
    parser = argparse.ArgumentParser(description="Save Share client for KNULLI handhelds")
    parser.add_argument("command", choices=["index", "scan", "upload", "browse", "download"], help="Action to run")
    parser.add_argument("--config", default="config.json", dest="config_path", help="Path to config file")
    args = parser.parse_args()

    config = Config.load(args.config_path)
    rom_index = build_index(config)

    if args.command == "index":
        return
    if args.command == "scan":
        scan_saves(config, rom_index)
    elif args.command == "upload":
        upload_flow(config, rom_index)
    elif args.command == "browse":
        browse_flow(config, rom_index)
    elif args.command == "download":
        download_cli(config, rom_index)


if __name__ == "__main__":
    main()


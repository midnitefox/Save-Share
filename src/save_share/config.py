import json
import os
from dataclasses import dataclass, field
from typing import Dict


DEFAULT_CONFIG = {
    "supabase_url": "https://your-project.supabase.co",
    "supabase_key": "public-anon-key",
    "roms_path": "/userdata/roms",
    "saves_path": "/userdata/saves",
    "log_path": "/userdata/system/logs/save-share.log",
    "cache_path": "/userdata/system/configs/save-share/cache.json",
    "device_nickname": "knulli-user",
}


@dataclass
class Config:
    supabase_url: str = DEFAULT_CONFIG["supabase_url"]
    supabase_key: str = DEFAULT_CONFIG["supabase_key"]
    roms_path: str = DEFAULT_CONFIG["roms_path"]
    saves_path: str = DEFAULT_CONFIG["saves_path"]
    log_path: str = DEFAULT_CONFIG["log_path"]
    cache_path: str = DEFAULT_CONFIG["cache_path"]
    device_nickname: str = DEFAULT_CONFIG["device_nickname"]
    extra: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        data = DEFAULT_CONFIG.copy()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                data.update({k: v for k, v in loaded.items() if v is not None})
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__}, extra=data)

    def save_example(self, path: str = "config.example.json") -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)


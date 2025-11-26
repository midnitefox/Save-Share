import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests


@dataclass
class RemoteSave:
    id: str
    system: str
    rom_hash: str
    rom_name: str
    save_type: str
    core: Optional[str]
    tags: List[str]
    description: str
    uploader: Optional[str]
    storage_path: str


class SupabaseClient:
    def __init__(self, url: str, key: str, session: Optional[requests.Session] = None):
        self.url = url.rstrip("/")
        self.key = key
        self.session = session or requests.Session()
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    def _rest_url(self, table: str) -> str:
        return f"{self.url}/rest/v1/{table}"

    def upsert_game(self, system: str, rom_hash: str, rom_name: str) -> Optional[str]:
        payload = [{"system": system, "rom_hash": rom_hash, "rom_name": rom_name}]
        resp = self.session.post(
            self._rest_url("games"),
            headers={**self.headers, "Prefer": "return=representation"},
            data=json.dumps(payload),
        )
        if resp.status_code not in (200, 201):
            return None
        data = resp.json()
        if data:
            return data[0].get("id")
        # fetch existing
        resp = self.session.get(
            self._rest_url("games"),
            headers=self.headers,
            params={"system": f"eq.{system}", "rom_hash": f"eq.{rom_hash}"},
        )
        if resp.ok and resp.json():
            return resp.json()[0].get("id")
        return None

    def upload_save_metadata(
        self,
        game_id: str,
        save_type: str,
        core: Optional[str],
        tags: List[str],
        description: str,
        uploader: Optional[str],
        storage_path: str,
        save_id: Optional[str] = None,
    ) -> Optional[str]:
        payload = {
            "id": save_id,
            "game_id": game_id,
            "save_type": save_type,
            "core": core,
            "tags": tags,
            "description": description,
            "uploader_nickname": uploader,
            "storage_path": storage_path,
        }
        resp = self.session.post(
            self._rest_url("saves"),
            headers={**self.headers, "Prefer": "return=representation"},
            data=json.dumps(payload),
        )
        if resp.status_code not in (200, 201):
            return None
        data = resp.json()
        return data[0].get("id") if data else None

    def upload_binary(self, bucket: str, storage_path: str, data: bytes) -> bool:
        upload_url = f"{self.url}/storage/v1/object/{bucket}/{storage_path}"
        resp = self.session.post(upload_url, headers=self.headers, data=data)
        return resp.status_code in (200, 201)

    def list_remote_saves(self, filters: List[Dict[str, str]]) -> List[RemoteSave]:
        # filters is list of {system, rom_hash}
        if not filters:
            return []
        systems = ",".join(sorted({f['system'] for f in filters}))
        rom_hashes = ",".join(sorted({f['rom_hash'] for f in filters}))
        resp = self.session.get(
            self._rest_url("saves_view"),
            headers=self.headers,
            params={"system": f"in.({systems})", "rom_hash": f"in.({rom_hashes})"},
        )
        if not resp.ok:
            return []
        saves: List[RemoteSave] = []
        for row in resp.json():
            saves.append(
                RemoteSave(
                    id=str(row.get("id")),
                    system=row.get("system"),
                    rom_hash=row.get("rom_hash"),
                    rom_name=row.get("rom_name"),
                    save_type=row.get("save_type"),
                    core=row.get("core"),
                    tags=row.get("tags") or [],
                    description=row.get("description") or "",
                    uploader=row.get("uploader_nickname"),
                    storage_path=row.get("storage_path"),
                )
            )
        return saves

    def download_save(self, bucket: str, storage_path: str) -> Optional[bytes]:
        url = f"{self.url}/storage/v1/object/{bucket}/{storage_path}"
        resp = self.session.get(url, headers=self.headers)
        if resp.ok:
            return resp.content
        return None


"""Object storage port and local implementation."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Protocol

from arg.config import Settings


class StoragePort(Protocol):
    def put_staging(self, key: str, data: bytes, metadata: dict | None = None) -> str: ...
    def promote(self, staging_ref: str, content_hash: str) -> str: ...
    def get_local_path(self, storage_ref: str) -> Path: ...
    def read_bytes(self, storage_ref: str) -> bytes: ...
    def delete(self, storage_ref: str) -> None: ...


class LocalStorage:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.root = settings.storage_root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if ".." in key.split("/") or key.startswith("/"):
            raise ValueError("storage key must be relative and safe")
        return self.root / key

    def put_staging(self, key: str, data: bytes, metadata: dict | None = None) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def promote(self, staging_ref: str, content_hash: str) -> str:
        staging_path = self._path(staging_ref)
        if not staging_path.exists():
            raise FileNotFoundError(staging_ref)
        final_key = f"content/{content_hash.replace('sha256:', '')}"
        final_path = self._path(final_key)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if not final_path.exists():
            shutil.copyfile(staging_path, final_path)
        return final_key

    def get_local_path(self, storage_ref: str) -> Path:
        return self._path(storage_ref)

    def read_bytes(self, storage_ref: str) -> bytes:
        return self._path(storage_ref).read_bytes()

    def delete(self, storage_ref: str) -> None:
        path = self._path(storage_ref)
        if path.exists():
            path.unlink()

    @staticmethod
    def sha256(data: bytes) -> str:
        return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return LocalStorage.sha256(data)

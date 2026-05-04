from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import tomllib


class AuthResolver:
    @staticmethod
    def resolve(api_key: str | None = None) -> str:
        if api_key:
            return api_key

        env_key = os.environ.get("MNEMOS_API_KEY")
        if env_key:
            return env_key

        config_key = AuthResolver._from_mnemos_config(Path.home() / ".mnemos" / "config.toml")
        if config_key:
            return config_key

        master_key = AuthResolver._from_api_keys_master(Path.home() / ".api_keys_master.json")
        if master_key:
            return master_key

        raise ValueError(
            "MNEMOS API key not found. Provide api_key, set MNEMOS_API_KEY, add api_key to "
            "~/.mnemos/config.toml, or set mnemos.bridge.api_key in ~/.api_keys_master.json."
        )

    @staticmethod
    def _from_mnemos_config(path: Path) -> str | None:
        if not path.exists():
            return None
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        value = data.get("api_key")
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _from_api_keys_master(path: Path) -> str | None:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            data: dict[str, Any] = json.load(handle)

        node: Any = data
        for key in ("mnemos", "bridge", "api_key"):
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node if isinstance(node, str) and node else None

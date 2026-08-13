#!/usr/bin/env python3

import json
import os
import sys

CONFIG_ENV = "ATLAS_CONFIG"


def valid_env_name(name: str) -> bool:
    if not name or not (name[0].isalpha() or name[0] == "_"):
        return False
    return all(char.isalnum() or char == "_" for char in name)


def load_config() -> None:
    raw = os.environ.get(CONFIG_ENV)
    if raw is None or not raw.strip():
        return

    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid {CONFIG_ENV} JSON: {exc}") from exc

    if not isinstance(config, dict):
        raise TypeError(f"{CONFIG_ENV} must contain a JSON object")

    for key, value in config.items():
        if not isinstance(key, str) or not valid_env_name(key):
            raise RuntimeError(f"invalid environment variable name: {key!r}")
        if key == CONFIG_ENV:
            raise RuntimeError(f"{CONFIG_ENV} cannot contain itself")
        if value is None:
            continue
        if not isinstance(value, str):
            raise TypeError(f"environment variable {key!r} must be a string")
        os.environ[key] = value

    os.environ.pop(CONFIG_ENV, None)


def main() -> int:
    if len(sys.argv) < 2:
        print("atlas-runtime: no application command provided", file=sys.stderr)
        return 1

    try:
        load_config()
    except RuntimeError as exc:
        print(f"atlas-runtime: {exc}", file=sys.stderr)
        return 1

    os.execvp(sys.argv[1], sys.argv[1:])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from pathlib import Path
import tomllib


parsed_config = None


def load_config():
    global parsed_config
    path = Path("~/.config/qlu/config.toml").expanduser()
    with open(path, "rb") as f:
        parsed_config = tomllib.load(f)
    return parsed_config

#!/usr/bin/env python3

from pathlib import Path
import tomllib


confbase = Path("~/.config/qlu/").expanduser()
confpath = confbase.joinpath("config.toml")
parsed_config = None


def load_config():
    global parsed_config
    if not confbase.exists():
        confbase.mkdir()
    if not confpath.exists():
        confpath.touch()
    with open(confpath, "rb") as f:
        parsed_config = tomllib.load(f)
    return parsed_config

""""Slob engine"""
from os import path
from pathlib import Path
from slob import open as slopen, find


class SlobEngine:


    def __init__(self) -> None:
        self.slobs = {}
        for name in Path(path.expanduser('~/.local/share/qlu/dicts/')).glob('*.slob'):
            slob = slopen(str(name))
            self.slobs[slob.id] = slob


    def query(self, keyword):
        results = find(keyword, self.slobs.values())
        return results

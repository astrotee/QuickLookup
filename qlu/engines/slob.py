""" "Slob engine"""

from os import path
from urllib.parse import urlparse
from pathlib import Path
from slob import open as slopen, find


class SlobEngine:
    SCHEME = "slob"

    def __init__(self) -> None:
        self.slobs = {}
        for name in Path(path.expanduser("~/.local/share/qlu/dicts/")).glob("*.slob"):
            slob = slopen(str(name))
            self.slobs[slob.id] = slob

    def query(self, keyword: str):
        results = find(keyword, self.slobs.values())
        for slob, item in results:
            result = {}
            result["id"] = f"slob://{slob.id}/{item.key}?blob={item.id}#{item.fragment}"
            result["key"] = item.key
            result["label"] = slob.tags.get("label")
            result["content"] = item.content.decode("utf-8")
            yield result

    def get(self, uri: str):
        parsed = urlparse(uri)
        assert parsed.scheme == "slob"
        slob_id = parsed.netloc
        item_key = parsed.path
        item_id = int(parsed.query.lstrip("blob="))
        return self.slobs[slob_id].get(item_id)

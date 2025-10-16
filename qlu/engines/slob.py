""" "Slob engine"""

from os import path
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from slob import open as slopen, find


class SlobEngine:
    SCHEME = "slob"
    URIS = {}

    def __init__(self) -> None:
        self.slobs = {}
        for name in Path(path.expanduser("~/.local/share/qlu/dicts/")).glob("*.slob"):
            slob = slopen(str(name))
            self.slobs[slob.id] = slob
            uri = slob.tags.get("uri")
            if uri:
                netloc = urlparse(uri).netloc
                slobs = self.URIS.setdefault(netloc, [])
                slobs.append(slob)

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
        assert parsed.scheme == "slob" or parsed.netloc in self.URIS
        slob_id = parsed.netloc
        item_key = parsed.path
        parsed_query = parse_qs(parsed.query) if parsed.query else None
        if parsed.scheme == "slob" and parsed_query and "blob" in parsed_query:
            item_id = int(parsed_query["blob"][0])
            result = self.slobs[slob_id].get(item_id)
        elif slob_id in self.URIS:
            key = item_key.split("/")[-1]
            results = find(key, self.URIS[slob_id])
            _, item = next(results)
            result = item.content_type, item.content
        else:
            raise KeyError()
        return result[0], result[1].decode("utf-8")

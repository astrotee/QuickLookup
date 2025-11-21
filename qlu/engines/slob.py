"""Slob engine"""

import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import cherrypy
from slob import find
from slob import open as slopen

from qlu.config import load_config

NOTHING_FOUND = (
    '<div align="center"><em>Nothing found for <strong>{0}</strong></em></div>'
)


class SlobEngine:
    SCHEME = "slob"
    BASE = "/slob"
    URIS = {}

    def __init__(self) -> None:
        self.config = self.get_config()
        path = self.config.get("path", "~/.local/share/qlu/dicts/")
        files = Path(path).expanduser().glob("*.slob")

        def sortkey(f):
            index = 0
            for index, name in enumerate(self.config["order"]):
                if name.lower() in f.name.lower():
                    return index
            return len(self.config["order"])

        if "order" in self.config:
            files = sorted(files, key=sortkey)
        self.slobs = OrderedDict()
        for name in files:
            slob = slopen(str(name))
            self.slobs[slob.id] = slob
            uri = slob.tags.get("uri")
            if uri:
                netloc = urlparse(uri).netloc
                slobs = self.URIS.setdefault(netloc, [])
                slobs.append(slob)
            self.handler = Root(self.slobs)

    def get_config(self):
        c = load_config()
        if c and "engines" in c and "slob" in c["engines"]:
            return c["engines"]["slob"]
        return {}

    def query(self, keyword: str):
        results = find(keyword, self.slobs.values())
        for slob, item in results:
            qkey = quote(item.key, "")
            result = {}
            result["id"] = f"slob://{slob.id}/{qkey}?blob={item.id}#{item.fragment}"
            result["key"] = item.key
            result["label"] = slob.tags.get("label")
            result["link"] = (
                f"http://localhost:8023/slob/{slob.id}/{qkey}?blob={item.id}#{item.fragment}"
            )
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


@cherrypy.expose
class Root:
    def __init__(self, slobs) -> None:
        self.slobs = slobs

    def find_slob(self, id_or_uri):
        if id_or_uri in self.slobs:
            slob = self.slobs[id_or_uri]
            uri = slob.tags.get("uri")
            netloc = urlparse(uri).netloc
            if netloc and netloc in SlobEngine.URIS:
                return slob, SlobEngine.URIS[netloc]
            return slob, None
        elif id_or_uri in SlobEngine.URIS:
            return None, SlobEngine.URIS[id_or_uri]
        return None, None

    def GET(self, *args, key=None, blob=None, **_):
        if len(args) < 2:
            raise cherrypy.NotFound()
        blob_id = blob

        if len(args) >= 2:
            key = "/".join(args[1:])

        slob_id_or_uri = args[0]
        if_none_match = cherrypy.request.headers.get("If-None-Match")
        slob, slobs = self.find_slob(slob_id_or_uri)

        if not slob and blob_id:
            raise cherrypy.NotFound
        elif slob and blob_id:
            content_type, content = slob.get(int(blob_id))
            cherrypy.response.headers["Content-Type"] = content_type
            cherrypy.response.headers["Cache-Control"] = "max-age=31556926"
            return content

        if key and if_none_match:
            e_tag = '"{}"'.format(slob_id_or_uri)
            if if_none_match == e_tag:
                cherrypy.response.status = 304
                return

        search_slobs = [slob]
        if slobs:
            search_slobs.extend(slobs)

        for slb, item in find(key, search_slobs, match_prefix=False):
            if slb is None:
                continue
            cherrypy.response.headers["X-URI"] = slb.tags.get("uri")
            cherrypy.response.headers["X-id"] = slb.id
            if slob:
                cherrypy.response.headers["Cache-Control"] = "max-age=31556926"
            else:
                cherrypy.response.headers["Cache-Control"] = "max-age=600"
                e_tag = '"{}"'.format(slb.id)
                cherrypy.response.headers["ETag"] = e_tag
            cherrypy.response.headers["Content-Type"] = item.content_type

            return item.content

        cherrypy.response.status = 404
        return NOTHING_FOUND.format(key if key else blob).encode("utf-8")

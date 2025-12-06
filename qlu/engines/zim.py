"""ZIM engine"""

from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote, urlparse

import cherrypy
from libzim.reader import (
    Archive,
    set_cluster_cache_max_size,
)
from libzim.search import Query, Searcher
from libzim.suggestion import SuggestionSearcher

from qlu.config import load_config

NOTHING_FOUND = (
    '<div align="center"><em>Nothing found for <strong>{0}</strong></em></div>'
)


class ZimEngine:
    SCHEME = "zim"
    BASE = "/zim"
    URIS = {}

    def __init__(self) -> None:
        self.config = self.get_config()
        path = self.config.get("path", "~/.local/share/qlu/dicts/")
        files = Path(path).expanduser().glob("*.zim")
        set_cluster_cache_max_size(10 * (2**20))

        def sortkey(f):
            index = 0
            for index, name in enumerate(self.config["order"]):
                if name.lower() in f.name.lower():
                    return index
            return len(self.config["order"])

        def filter_files(f, includes):
            for name in includes:
                if name.lower() in f.name.lower():
                    return True
            return False

        if "include" in self.config:
            files = (f for f in files if filter_files(f, self.config["include"]))
        elif "exclude" in self.config:
            files = (f for f in files if not filter_files(f, self.config["exclude"]))
        if "order" in self.config:
            files = sorted(files, key=sortkey)
        self.zims = OrderedDict()
        for name in files:
            zim = Archive(name)
            self.zims[str(zim.uuid)] = zim
            if "Source" in zim.metadata_keys:
                source = zim.get_metadata("Source")
                netloc = str(urlparse(source).netloc)
                zims = self.URIS.setdefault(netloc, [])
                zims.append(zim)

        self.handler = Root(self.zims)

    def get_config(self):
        c = load_config()
        if c and "engines" in c and "zim" in c["engines"]:
            return c["engines"]["zim"]
        return {}

    def query(self, keyword: str):
        fts = bool(self.config.get("fts", True))
        for id, archive in self.zims.items():
            if fts:
                searcher = Searcher(archive)
                query = Query().set_query(keyword)
                search = searcher.search(query)
            else:
                suggestions_searcher = SuggestionSearcher(archive)
                search = suggestions_searcher.suggest(keyword)
            for path in search.getResults(0, 10):
                qpath = path[:2] + quote(path[2:], safe="")
                entry = archive.get_entry_by_path(path)
                item = entry.get_item()
                result = {}
                result["id"] = f"zim://{id}/{path}"
                result["key"] = item.title.strip()
                result["label"] = archive.get_metadata("Title").decode("utf-8")
                result["link"] = f"http://localhost:8023/zim/{id}/{qpath}"
                yield result

    def get(self, uri: str):
        parsed = urlparse(uri)
        assert parsed.scheme == "zim"
        archive_id = parsed.netloc
        path = parsed.path
        if archive_id not in self.zims:
            raise KeyError(f"Archive {archive_id} not found!")
        if not self.zims[archive_id].has_entry_by_path(path):
            raise KeyError(f"path '{path}' not found!")
        entry = self.zims[archive_id].get_entry_by_path(path)
        item = entry.get_item()
        return item.mimetype, item.content


@cherrypy.expose
class Root:
    def __init__(self, zims) -> None:
        self.zims = zims

    def GET(self, *args, **_):
        if len(args) < 2:
            raise cherrypy.NotFound()

        path = "/".join(args[1:])

        archive_id = args[0]
        archive = self.zims[archive_id]
        if archive_id not in self.zims:
            print(f"archive {archive_id} not found!")
            raise cherrypy.NotFound()
        if not archive.has_entry_by_path(path):
            print(f"path {path} not found!")
            raise cherrypy.NotFound()
        entry = archive.get_entry_by_path(path)
        item = entry.get_item()
        cherrypy.response.headers["Content-Type"] = item.mimetype
        cherrypy.response.headers["Cache-Control"] = "max-age=31556926"
        return item.content

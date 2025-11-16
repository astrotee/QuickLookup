#!/usr/bin/env python3
import argparse
import atexit
import os
import readline
from itertools import chain
from urllib.parse import urlparse

from html2text import html2text

from . import engines
from .config import load_config, confbase
from .picker import pick_pipe, pick
from .server import ServerContext


def set_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", nargs="*", help="the query used to lookup")
    group.add_argument("-g", "--get", dest="uri")
    group.add_argument("-H", "--history", action="store_true", help="pick from history")
    group.add_argument(
        "-B", "--bookmarks", action="store_true", help="pick from bookmarks"
    )
    parser.add_argument(
        "-f", dest="first", action="store_true", help="return the first result"
    )
    return parser.parse_args()


def init_readline():
    histfile = confbase.joinpath("search_history")
    readline.parse_and_bind('"\\C-xh": "qlu_history\n"')
    readline.parse_and_bind('"\\C-xb": "qlu_bookmarks\n"')
    readline.set_auto_history(False)

    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        open(histfile, "wb").close()

    atexit.register(readline.write_history_file, histfile)


def query(key):
    results = []
    for engine in engines:
        results.append(engine.query(key))
    return chain.from_iterable(results)


def get(uri):
    parsed = urlparse(uri)
    scheme = parsed.scheme
    for engine in engines:
        if engine.SCHEME == scheme or parsed.netloc in engine.URIS:
            return engine.get(uri)
    raise ValueError("engine not found!")


def loop(args):
    prompt = "> " if os.isatty(0) else ""
    if len(args.query) == 0:
        q = input(prompt)
    else:
        q = " ".join(args.query)
    while True:
        if q.startswith("qlu_"):
            if q == "qlu_history":
                pick(1)
            elif q == "qlu_bookmarks":
                pick(2)
            q = input(prompt)
            continue
        else:
            readline.add_history(q)

        results = query(q)

        if not os.isatty(1):
            pick_pipe(results)
            return

        if args.first:
            item = next(results)
        else:
            item = pick(results)
        q = input(prompt)


def main():
    args = set_args()
    load_config()
    init_readline()
    if args.uri:
        item = get(args.uri)[1]
        if os.isatty(1):
            print(html2text(item))
        else:
            print(item, flush=True)
        return

    with ServerContext():
        if args.history:
            pick(1)
        elif args.bookmarks:
            pick(2)
        else:
            loop(args)


if __name__ == "__main__":
    main()

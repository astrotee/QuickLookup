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
    parser.add_argument(
        "-f", dest="first", action="store_true", help="return the first result"
    )
    return parser.parse_args()


def init_readline():
    histfile = confbase.joinpath("search_history")

    try:
        readline.read_history_file(histfile)
        h_len = readline.get_current_history_length()
    except FileNotFoundError:
        open(histfile, "wb").close()
        h_len = 0

    def save(prev_h_len, histfile):
        new_h_len = readline.get_current_history_length()
        readline.set_history_length(1000)
        readline.append_history_file(new_h_len - prev_h_len, histfile)

    atexit.register(save, h_len, histfile)


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
            pick()
        else:
            loop(args)


if __name__ == "__main__":
    main()

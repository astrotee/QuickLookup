#!/usr/bin/env python3
import os
import argparse
from itertools import chain
from urllib.parse import urlparse
from html2text import html2text
from qlu import engines
from .server import ServerContext
from .picker import pick_iterfzf, pick_pipe
import readline


def set_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", nargs="*", help="the query used to lookup")
    group.add_argument("-g", "--get", dest="uri")
    parser.add_argument(
        "-f", dest="first", action="store_true", help="return the first result"
    )
    return parser.parse_args()


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
            item = pick_iterfzf(results)
        q = input(prompt)


def main():
    args = set_args()
    if args.uri:
        item = get(args.uri)[1]
        if os.isatty(1):
            print(html2text(item))
        else:
            print(item, flush=True)
        return

    with ServerContext():
        loop(args)


if __name__ == "__main__":
    main()

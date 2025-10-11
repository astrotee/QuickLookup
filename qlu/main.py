#!/usr/bin/env python3
import os
import argparse
from itertools import chain
from urllib.parse import urlparse
from html2text import html2text
from qlu import engines
import webview
from iterfzf import iterfzf


def set_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", nargs="+", help="the query used to lookup")
    group.add_argument("-g", "--get", dest="uri")
    parser.add_argument(
        "-f", dest="first", action="store_true", help="return the first result"
    )
    return parser.parse_args()


def display_content(item):
    # print(f"{item['label']}\t{item['key']}")
    # print(html2text(item["content"]))
    window = webview.create_window(
        f"{item['label']}-{item['key']}", html=item["content"]
    )
    webview.start()
    return


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


def pick_item(items):
    # items = list(items)
    # for i, item in enumerate(items):
    #     print(f"[{i}] {item['label']}\t{item['key']}")
    # i = int(input("> "))
    # return items[i]
    def transform():
        for i, item in enumerate(items):
            yield f"{item['id']}\x1e{item['label']}\x1e{item['key']}\x1e{item['content']}\0"

    choice = iterfzf(transform(), __extra__=["-d", "\036", "--with-nth", "{2}\t{3}"])
    print(choice)


def main():
    args = set_args()
    if args.uri:
        item = get(args.uri)[1]
        if os.isatty(1):
            print(html2text(item))
        else:
            print(item, flush=True)
        return

    results = query(" ".join(args.query))

    if not os.isatty(1):
        for r in results:
            # print(f"{r['id']}\t{r['key']}\t{r['label']}")
            print(
                f"{r['id']}\x1e{r['label']}\x1e{r['key']}\x1e{r['content']}",
                end="\0",
                flush=True,
            )
        return

    if args.first:
        item = next(results)
    else:
        item = pick_item(results)
    display_content(item)


if __name__ == "__main__":
    main()

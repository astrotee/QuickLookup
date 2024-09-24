#!/usr/bin/env python3
import argparse
from html2text import html2text
from qlu import engine


def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='+', help='the query used to lookup')
    parser.add_argument('-f', dest='first', action='store_true', help='return the first result')
    return parser.parse_args()

def display_content(blob, item):
    print(f"{blob.tags.get('label')}\t{item.key}")
    print(html2text(item.content.decode('utf-8')))
    return

def query(key):
    results = engine.query(' '.join(key))
    return results

def pick_item(items):
    items = list(items)
    for i, (blob, item) in enumerate(items):
        print(f"[{i}] {blob.tags.get('label')}\t{item.key}")
    i = int(input("> "))
    return items[i]

def main():
    args = set_args()
    results = query(' '.join(args.query))
    if args.first:
        blob, item = next(results)
        display_content(blob, item)
    else:
        item = pick_item(results)
        display_content(*item) 


if __name__ == "__main__":
    main()

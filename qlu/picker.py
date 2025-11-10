#!/usr/bin/env python3

from iterfzf import iterfzf



def row_generator(items, fields, /, fs="\t", rs=""):
    for item in items:
        row = [item[x] or "None" for x in fields if x in item]
        yield fs.join(row) + rs


def pick_iterfzf(items):
    try:
        choice = iterfzf(
            row_generator(items, ["id", "label", "key", "link"], "\x1e", "\0"),
            preview="w3m -T text/html -dump {4}",
            bind={
                "ctrl-f": "preview-page-down",
                "ctrl-b": "preview-page-up",
                "enter": "execute:(w3m -T text/html {4})",
            },
            __extra__=[
                "--reverse",
                "-d",
                "\036",
                "--with-nth",
                "{2} {3}",
                "--read0",
                "--accept-nth",
                "4",
                "--info=inline",
                "--preview-window=down,80%",
            ],
        )
        print(choice)
        return choice
    except KeyboardInterrupt:
        pass
    except AttributeError:
        print("Nothing Found!")


def pick_loop(items):
    items = list(items)
    for i, item in enumerate(items):
        print(f"[{i}] {item['label']}\t{item['key']}")
    i = int(input("> "))
    return items[i]


def pick_pipe(items):
    for r in row_generator(items, ["id", "label", "key", "link"], "\x1e", "\0"):
        print(r, flush=True)

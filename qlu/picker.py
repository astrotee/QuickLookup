#!/usr/bin/env python3

from iterfzf import iterfzf


def pick_iterfzf(items):
    def transform():
        for item in items:
            yield f"{item['id']}\x1e{item['label']}\x1e{item['key']}\x1e{item['link']}\0"

    try:
        choice = iterfzf(
            transform(),
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
    for r in items:
        print(
            "\x1e".join((r["id"], r["label"], r["key"], r["link"])),
            end="\0",
            flush=True,
        )

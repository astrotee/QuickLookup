#!/usr/bin/env python3

from iterfzf import iterfzf

from .config import parsed_config


def row_generator(items, fields, fs="\t", rs=""):
    for item in items:
        row = [item[x] or "None" for x in fields if x in item]
        yield fs.join(row) + rs


def pick_iterfzf(items):
    config = parsed_config.get("picker", {}).get("fzf", {})
    fields = config.get("fields", ["id", "key", "label", "link"])
    delimeter = config.get("delimeter", "\t")
    rs = config.get("rs", "")
    preview = config.get("preview", "w3m -T text/html -dump {4}")
    binds = {
        "ctrl-f": "preview-page-down",
        "ctrl-b": "preview-page-up",
        "enter": "execute(w3m -T text/html {4})",
    }
    binds_config = config.get("binds", {})
    binds.update(binds_config)
    options = config.get("options", [])
    try:
        choice = iterfzf(
            row_generator(items, fields, delimeter, rs),
            preview=preview,
            bind=binds,
            __extra__=[
                "--reverse",
                "-d",
                delimeter,
                "--with-nth",
                "{2} {3}",
                "--accept-nth",
                "4",
                "--info=inline",
                "--preview-window=down,80%",
            ]
            + options,
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
    config = parsed_config.get("picker", {}).get("pipe", {})
    fields = config.get("fields", ["id", "key", "label", "link"])
    delimeter = config.get("delimeter", "\x1e")
    rs = config.get("rs", "\0")
    for r in row_generator(items, fields, delimeter, rs):
        print(r, flush=True, end="")

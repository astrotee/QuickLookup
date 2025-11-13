#!/usr/bin/env python3

from typing import Iterable
from iterfzf import iterfzf

from .config import parsed_config, confbase


def row_generator(items, fields, fs="\t", rs=""):
    for item in items:
        row = [item[x] or "None" for x in fields if x in item]
        yield fs.join(row) + rs


def iter_file(file):
    with open(file, "rb") as f:
        for line in f:
            yield line.strip()


def pick(input: int | Iterable):
    """if input is 1 pick from the history file
    if input is 2 pick from the bookmarks file
    else it's a Iterable to iterate"""
    config = parsed_config.get("picker", {})
    fields = config.get("fields", ["id", "key", "label", "link"])
    delimeter = config.get("delimeter", "\t")
    rs = config.get("rs", "")
    if input == 1:
        histfile = confbase.joinpath("picker_history")
        i = iter_file(histfile)
    elif input == 2:
        bmfile = confbase.joinpath("bookmarks")
        i = iter_file(bmfile)
    else:
        i = row_generator(input, fields, delimeter, rs)
    pick_iterfzf(i, config, input is not None)


def pick_iterfzf(iterator, config, history=True):
    bmfile = confbase.joinpath("bookmarks")
    delimeter = config.get("delimeter", "\t")
    fzfconfig = parsed_config.get("fzf", {})
    preview = fzfconfig.get("preview", "w3m -T text/html -dump {4}")
    binds = {
        "ctrl-f": "preview-page-down",
        "ctrl-b": "preview-page-up",
        "enter": "execute(w3m -T text/html {4})",
        "alt-b": f"execute(echo {{}} >> {bmfile})",
    }
    binds_config = fzfconfig.get("binds", {})
    binds.update(binds_config)
    if history:
        histfile = confbase.joinpath("picker_history")
        if "enter" in binds and not binds["enter"].isspace():
            binds["enter"] = f"execute(echo {{}} >> {histfile})+" + binds["enter"]
        else:
            binds["enter"] = f"execute(echo {{}} >> {histfile})"
    options = [
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
    options_config = config.get("options", [])
    options.extend(options_config)
    try:
        choice = iterfzf(
            iterator,
            preview=preview,
            bind=binds,
            __extra__=options,
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

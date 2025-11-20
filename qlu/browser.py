#!/usr/bin/env python3

import webbrowser

from html2text import html2text


def display_webview(item):
    try:
        import webview
    except ImportError:
        raise ImportError("pywebview is not installed!")
    window = webview.create_window(
        f"{item['label']}-{item['key']}", html=item["content"]
    )
    webview.start()


def display_text(item):
    print(f"{item['label']}\t{item['key']}")
    print(html2text(item["content"]))


def display_webbrowser(item):
    webbrowser.open(item["link"])

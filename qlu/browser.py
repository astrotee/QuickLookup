#!/usr/bin/env python3


import webview
from html2text import html2text


def display_webview(item):
    window = webview.create_window(
        f"{item['label']}-{item['key']}", html=item["content"]
    )
    webview.start()


def display_text(item):
    print(f"{item['label']}\t{item['key']}")
    print(html2text(item["content"]))

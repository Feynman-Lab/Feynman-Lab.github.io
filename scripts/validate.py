#!/usr/bin/env python3
"""Check generated locale pages, navigation, SEO links, and email targets."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("en", "zh-CN", "ja", "es", "pt-BR", "fr", "de")
PAGES = ("", "projects", "submit", "about")
BASE = "https://feynman-lab.github.io"


def route(locale: str, page: str) -> str:
    prefix = "" if locale == "en" else f"/{locale}"
    return f"{prefix}/{page + '/' if page else ''}"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = None
        self.canonical = None
        self.alternates = {}
        self.links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang")
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href")
        if tag == "link" and data.get("rel") == "alternate":
            self.alternates[data.get("hreflang")] = data.get("href")
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])


def main() -> None:
    translations = json.loads((ROOT / "scripts" / "translations.json").read_text(encoding="utf-8"))
    assert set(translations) == set(LOCALES)
    english_keys = set(translations["en"])
    assert all(set(copy) == english_keys for copy in translations.values())
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for locale in LOCALES:
        for page in PAGES:
            current = route(locale, page)
            file = ROOT / current.lstrip("/") / "index.html" if current != "/" else ROOT / "index.html"
            assert file.is_file(), file
            parser = PageParser()
            parser.feed(file.read_text(encoding="utf-8"))
            assert parser.lang == locale, file
            assert parser.canonical == BASE + current, file
            assert f"<loc>{BASE + current}</loc>" in sitemap, file
            expected = {language: BASE + route(language, page) for language in LOCALES}
            expected["x-default"] = BASE + route("en", page)
            assert parser.alternates == expected, file
            for href in parser.links:
                if href.startswith("/"):
                    target = ROOT / href.lstrip("/") / "index.html" if href != "/" else ROOT / "index.html"
                    assert target.is_file(), (file, href)
            if page == "submit":
                mailto = next(link for link in parser.links if link.startswith("mailto:"))
                parsed = urlparse(mailto)
                assert parsed.path == "torres4koo@gmail.com", file
                assert parse_qs(parsed.query).get("body"), file
    print("Validated 28 pages, translations, navigation, SEO links, and email drafts")


if __name__ == "__main__":
    main()

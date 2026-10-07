#!/usr/bin/env python3
"""Check generated locale pages, navigation, SEO links, and email targets."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import struct
import xml.etree.ElementTree as ET

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
        self.assets = []
        self.ids = set()
        self.h1_count = 0
        self.meta = {}
        self.structured_data = []
        self._in_structured_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "html":
            self.lang = data.get("lang")
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href")
        if tag == "link" and data.get("rel") == "alternate":
            self.alternates[data.get("hreflang")] = data.get("href")
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "link" and data.get("rel") in {"stylesheet", "icon"}:
            self.assets.append(data.get("href"))
        if tag == "script" and data.get("src"):
            self.assets.append(data["src"])
        if tag == "meta":
            self.meta[data.get("name") or data.get("property")] = data.get("content")
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_structured_data = True

    def handle_data(self, data: str) -> None:
        if self._in_structured_data:
            self.structured_data.append(json.loads(data))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_structured_data = False


def main() -> None:
    translations = json.loads((ROOT / "scripts" / "translations.json").read_text(encoding="utf-8"))
    assert set(translations) == set(LOCALES)
    english_keys = set(translations["en"])
    assert all(set(copy) == english_keys for copy in translations.values())
    sitemap = ET.parse(ROOT / "sitemap.xml")
    mapped_urls = {
        loc.text for loc in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    assert len(mapped_urls) == 21, mapped_urls
    og_image = ROOT / "assets" / "og-image.png"
    logo = ROOT / "assets" / "logo-512.png"
    assert og_image.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", og_image.read_bytes()[16:24]) == (1200, 630)
    assert struct.unpack(">II", logo.read_bytes()[16:24]) == (512, 512)
    for locale in LOCALES:
        for page in PAGES:
            current = route(locale, page)
            file = ROOT / current.lstrip("/") / "index.html" if current != "/" else ROOT / "index.html"
            assert file.is_file(), file
            parser = PageParser()
            parser.feed(file.read_text(encoding="utf-8"))
            assert parser.lang == locale, file
            assert parser.h1_count == 1, file
            assert "main-content" in parser.ids and "#main-content" in parser.links, file
            assert parser.canonical == BASE + current, file
            if page == "projects":
                assert parser.meta.get("robots") == "noindex,follow", file
                assert BASE + current not in mapped_urls, file
            else:
                assert parser.meta.get("robots") is None, file
                assert BASE + current in mapped_urls, file
            assert parser.meta.get("og:site_name") == "Feynman Lab", file
            assert parser.meta.get("og:image") == BASE + "/assets/og-image.png", file
            assert parser.meta.get("twitter:card") == "summary_large_image", file
            assert parser.meta.get("twitter:image") == BASE + "/assets/og-image.png", file
            expected = {language: BASE + route(language, page) for language in LOCALES}
            expected["x-default"] = BASE + route("en", page)
            assert parser.alternates == expected, file
            for href in parser.links:
                if href.startswith("#"):
                    assert href[1:] in parser.ids, (file, href)
                if href.startswith("/"):
                    target = ROOT / href.lstrip("/") / "index.html" if href != "/" else ROOT / "index.html"
                    assert target.is_file(), (file, href)
            for asset in parser.assets:
                if asset.startswith("/"):
                    assert (ROOT / asset.lstrip("/")).is_file(), (file, asset)
            if page == "submit":
                mailto = next(link for link in parser.links if link.startswith("mailto:"))
                parsed = urlparse(mailto)
                assert parsed.path == "torres4koo@gmail.com", file
                assert parse_qs(parsed.query).get("body"), file
            if locale == "en" and page == "":
                graph = parser.structured_data[0]["@graph"]
                assert {node["@type"] for node in graph} == {"Organization", "WebSite"}
                assert next(node for node in graph if node["@type"] == "Organization")["sameAs"] == ["https://github.com/Feynman-Lab"]
    print("Validated 28 pages, 21 indexable URLs, metadata, assets, navigation, accessibility anchors, and email drafts")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build every localized page as plain HTML for GitHub Pages."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://feynman-lab.github.io"
EMAIL = "torres4koo@gmail.com"
PAGES = ("", "projects", "submit", "about")
LANGUAGES = {
    "en": ("🇺🇸", "English", "EN"),
    "zh-CN": ("🇨🇳", "简体中文", "中文"),
    "ja": ("🇯🇵", "日本語", "日本語"),
    "es": ("🇪🇸", "Español", "ES"),
    "pt-BR": ("🇧🇷", "Português", "PT"),
    "fr": ("🇫🇷", "Français", "FR"),
    "de": ("🇩🇪", "Deutsch", "DE"),
}

TRANSLATIONS = json.loads((ROOT / "scripts" / "translations.json").read_text(encoding="utf-8"))
required = set(TRANSLATIONS["en"])
for code in LANGUAGES:
    missing = required - set(TRANSLATIONS[code])
    extra = set(TRANSLATIONS[code]) - required
    if missing or extra:
        raise ValueError(f"{code}: missing={sorted(missing)}, extra={sorted(extra)}")


def route(locale: str, page: str = "") -> str:
    prefix = "" if locale == "en" else f"/{locale}"
    return f"{prefix}/{page + '/' if page else ''}"


def tr(locale: str, key: str) -> str:
    return escape(TRANSLATIONS[locale][key])


def brand(locale: str) -> str:
    return (
        f'<a class="brand" href="{route(locale)}">'
        '<svg class="brand-mark" viewBox="0 0 64 64" fill="none" aria-hidden="true">'
        '<path d="M12 51V13h30M12 31h22" stroke="currentColor" stroke-width="4"/>'
        '<path d="M36 13c9 1 14 8 13 17-1 10-9 19-19 21" stroke="#668CC1" stroke-width="2"/>'
        '<circle cx="49" cy="29" r="4" fill="#668CC1"/>'
        '<circle cx="30" cy="51" r="3" fill="currentColor"/></svg>Feynman Lab</a>'
    )


def language_menu(locale: str, page: str) -> str:
    flag, _, short = LANGUAGES[locale]
    options = ""
    for code, (option_flag, name, _) in LANGUAGES.items():
        current = ' aria-current="true"' if code == locale else ""
        options += (
            f'<a href="{route(code, page)}" lang="{code}" hreflang="{code}"{current}>'
            f'<span aria-hidden="true">{option_flag}</span>{escape(name)}</a>'
        )
    return (
        f'<details class="language-menu"><summary aria-label="{tr(locale, "language_label")}">'
        f'<span aria-hidden="true">{flag}</span> {escape(short)} <span class="chevron" aria-hidden="true">⌄</span>'
        f'</summary><div class="language-options">{options}</div></details>'
    )


def header(locale: str, page: str) -> str:
    project_current = ' aria-current="page"' if page == "projects" else ""
    submit_current = ' aria-current="page"' if page == "submit" else ""
    return (
        '<header class="site-header"><div class="wrap header-inner">'
        + brand(locale)
        + f'<nav class="nav" aria-label="{tr(locale, "main_navigation")}">'
        + f'<a href="{route(locale, "projects")}"{project_current}>{tr(locale, "nav_projects")}</a>'
        + '<a class="github-link" href="https://github.com/Feynman-Lab" target="_blank" rel="noopener noreferrer">GitHub ↗</a>'
        + language_menu(locale, page)
        + f'<a class="button small" href="{route(locale, "submit")}"{submit_current}>{tr(locale, "nav_submit")} <span class="arrow" aria-hidden="true">↗</span></a>'
        + '</nav></div></header>'
    )


def footer(locale: str) -> str:
    links = "".join(
        f'<a href="{route(locale, page)}">{tr(locale, key)}</a>'
        for page, key in (("projects", "nav_projects"), ("submit", "nav_submit"), ("about", "nav_about"))
    )
    return (
        '<footer class="site-footer"><div class="wrap"><div class="footer-top"><div>'
        + brand(locale)
        + f'<p>{tr(locale, "tagline")}</p></div>'
        + f'<nav class="footer-links" aria-label="{tr(locale, "footer_navigation")}">{links}'
        + '<a href="https://github.com/Feynman-Lab" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav></div>'
        + f'<div class="footer-bottom"><span>© 2026 Feynman Lab</span><span>{tr(locale, "footer_line")}</span></div>'
        + '</div></footer>'
    )


def head(locale: str, page: str) -> str:
    title_key = {"": "meta_home_title", "projects": "meta_projects_title", "submit": "meta_submit_title", "about": "meta_about_title"}[page]
    description_key = {"": "meta_home_description", "projects": "meta_projects_description", "submit": "meta_submit_description", "about": "meta_about_description"}[page]
    canonical = BASE + route(locale, page)
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{BASE + route(code, page)}">'
        for code in LANGUAGES
    ) + f'<link rel="alternate" hreflang="x-default" href="{BASE + route("en", page)}">'
    return (
        '<!doctype html><html lang="' + locale + '"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="theme-color" content="#f7f9fc">'
        f'<meta name="description" content="{tr(locale, description_key)}">'
        f'<link rel="canonical" href="{canonical}">{alternates}'
        '<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">'
        '<link rel="stylesheet" href="/assets/site.css">'
        '<script src="/assets/motion.js" defer></script>'
        '<meta property="og:type" content="website">'
        f'<meta property="og:title" content="{tr(locale, title_key)}">'
        f'<meta property="og:description" content="{tr(locale, description_key)}">'
        f'<meta property="og:url" content="{canonical}">'
        f'<title>{tr(locale, title_key)}</title></head><body>'
    )


def diagram(locale: str) -> str:
    return (
        '<div class="diagram" aria-hidden="true"><svg viewBox="0 0 500 500" role="presentation">'
        '<path class="axis" d="M46 250H454M250 46V454"/><circle class="axis" cx="250" cy="250" r="180"/>'
        '<circle class="axis" cx="250" cy="250" r="113"/>'
        '<g class="orbit-rotor">'
        '<path class="orbit" d="M87 335C108 405 211 442 295 390S422 250 382 163 232 83 154 147 93 266 187 286 328 219 331 165"/>'
        '<path class="orbit" d="M96 169c31-91 142-129 235-81 87 46 110 147 69 229-35 70-122 111-204 82"/>'
        '</g>'
        '<circle class="point" cx="87" cy="335" r="7"/><circle class="point" cx="382" cy="163" r="6"/>'
        '<circle class="point-soft" cx="331" cy="165" r="4"/><circle class="point-soft" cx="196" cy="399" r="4"/>'
        '<circle class="diagram-core" cx="250" cy="250" r="9"/>'
        f'<text class="note" x="56" y="359">{tr(locale, "diagram_idea")}</text>'
        f'<text class="note" x="383" y="145">{tr(locale, "diagram_build")}</text>'
        '<text class="note" x="267" y="246">LAB</text></svg></div>'
    )


def home(locale: str) -> str:
    t = lambda key: tr(locale, key)
    submit = route(locale, "submit")
    projects = route(locale, "projects")
    about = route(locale, "about")
    steps = "".join(
        f'<div class="step"><span class="step-num">0{i} / {t(f"step{i}_label")}</span>'
        f'<h3>{t(f"step{i}_title")}</h3><p>{t(f"step{i}_text")}</p></div>'
        for i in (1, 2, 3)
    )
    return f'''<main>
<section class="hero" aria-labelledby="hero-title"><canvas class="hero-field" aria-hidden="true"></canvas><div class="wrap hero-grid"><div class="hero-copy">
<div class="eyebrow">{t("home_eyebrow")}</div><h1 id="hero-title">{t("home_title_first")} <span>{t("home_title_second")}</span></h1>
<p>{t("home_intro")}</p><div class="hero-actions"><a class="button" href="{submit}">{t("nav_submit")} <span class="arrow" aria-hidden="true">↗</span></a><a class="text-link" href="{projects}">{t("home_see_projects")} <span aria-hidden="true">↗</span></a></div>
<div class="hero-footnote"><span class="line" aria-hidden="true"></span>{t("home_note")}</div></div>{diagram(locale)}</div></section>
<section class="section" id="how-it-works"><div class="wrap"><div class="section-head"><div><div class="eyebrow">{t("process_label")}</div><h2>{t("process_title")}</h2></div><p>{t("process_intro")}</p></div><div class="steps">{steps}</div></div></section>
<section class="section" id="projects"><div class="wrap"><div class="section-head"><div><div class="eyebrow">{t("projects_label")}</div><h2>{t("projects_title")}</h2></div><p>{t("projects_intro")}</p></div><div class="project-empty"><div class="empty-art" aria-hidden="true"><span class="cross">✳</span></div><div class="empty-copy"><span class="eyebrow">{t("projects_badge")}</span><h3>{t("projects_empty_title")}</h3><p>{t("projects_empty_text")}</p><a class="text-link" href="{submit}">{t("projects_cta")} <span aria-hidden="true">↗</span></a></div></div></div></section>
<section class="section"><div class="wrap philosophy"><div><div class="eyebrow">{t("why_label")}</div><p class="statement">{t("why_statement")}</p></div><div class="explain"><p>{t("why_p1")}</p><p>{t("why_p2")}</p><a class="text-link" href="{about}">{t("why_more")} <span aria-hidden="true">↗</span></a></div></div></section>
<section class="cta-section"><div class="wrap"><div class="cta-panel"><div><div class="eyebrow">{t("cta_label")}</div><h2>{t("cta_title")}</h2><p>{t("cta_text")}</p></div><a class="button light" href="{submit}">{t("nav_submit")} <span class="arrow" aria-hidden="true">↗</span></a></div></div></section>
</main>'''


def page_hero(locale: str, label: str, title: str, intro: str) -> str:
    return f'<section class="page-hero"><div class="wrap"><div class="eyebrow">{tr(locale, label)}</div><h1>{tr(locale, title)}</h1><p>{tr(locale, intro)}</p></div></section>'


def projects_page(locale: str) -> str:
    t = lambda key: tr(locale, key)
    return (
        '<main>' + page_hero(locale, "projects_label", "projects_title", "project_page_intro")
        + '<section class="page-content"><div class="wrap"><div class="project-empty">'
        + '<div class="empty-art" aria-hidden="true"><span class="cross">✳</span></div><div class="empty-copy">'
        + f'<span class="eyebrow">{t("projects_badge")}</span><h3>{t("project_page_empty_title")}</h3>'
        + f'<p>{t("project_page_empty_text")}</p><a class="text-link" href="{route(locale, "submit")}">{t("project_page_cta")} <span aria-hidden="true">↗</span></a>'
        + '</div></div></div></section></main>'
    )


def submit_page(locale: str) -> str:
    t = lambda key: tr(locale, key)
    body = "\n\n".join(TRANSLATIONS[locale][f"mail_prompt{i}"] for i in (1, 2, 3)) + "\n"
    mailto = f'mailto:{EMAIL}?subject={quote(TRANSLATIONS[locale]["mail_subject"])}&amp;body={quote(body)}'
    return f'''<main>{page_hero(locale, "submit_label", "submit_title", "submit_intro")}
<section class="page-content"><div class="wrap"><div class="submission-card"><div class="eyebrow">{t("submit_card_label")}</div><h2>{t("submit_card_title")}</h2><p>{t("submit_card_intro")}</p>
<ol><li>{t("submit_q1")}</li><li>{t("submit_q2")}</li><li>{t("submit_q3")}</li></ol>
<a class="button" href="{mailto}">{t("submit_email_button")} <span class="arrow" aria-hidden="true">↗</span></a>
<p class="fine-print">{t("submit_email_note")} <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<div class="alternate-submit"><span>{t("submit_public_intro")}</span><a class="text-link" href="https://github.com/Feynman-Lab/discussions/discussions/new" target="_blank" rel="noopener noreferrer">{t("submit_public_button")} <span aria-hidden="true">↗</span></a><p class="fine-print">{t("submit_public_note")}</p></div></div>
<div class="prose-grid next-steps"><div><h2>{t("submit_next_title")}</h2></div><div><p>{t("submit_next_p1")}</p><p>{t("submit_next_p2")}</p></div></div></div></section></main>'''


def about_page(locale: str) -> str:
    t = lambda key: tr(locale, key)
    return f'''<main>{page_hero(locale, "about_label", "about_title", "about_intro")}
<section class="page-content"><div class="wrap prose-grid"><div><h2>{t("about_heading")}</h2></div><div><p>{t("about_p1")}</p><p>{t("about_p2")}</p><p>{t("about_p3")}</p><a class="button" href="{route(locale, "submit")}">{t("about_cta")} <span class="arrow" aria-hidden="true">↗</span></a></div></div></section></main>'''


def main() -> None:
    renderers = {"": home, "projects": projects_page, "submit": submit_page, "about": about_page}
    urls = []
    for locale in LANGUAGES:
        for page in PAGES:
            target = ROOT / route(locale, page).lstrip("/") / "index.html" if route(locale, page) != "/" else ROOT / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(head(locale, page) + header(locale, page) + renderers[page](locale) + footer(locale) + '</body></html>\n', encoding="utf-8")
            urls.append(BASE + route(locale, page))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{url}</loc></url>\n" for url in urls)
    (ROOT / "sitemap.xml").write_text(sitemap + "</urlset>\n", encoding="utf-8")
    print(f"Built {len(urls)} pages in {len(LANGUAGES)} languages")


if __name__ == "__main__":
    main()

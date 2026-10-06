# Feynman Lab website

The static source for [feynman-lab.github.io](https://feynman-lab.github.io/).

GitHub Pages publishes the root of `main`. The HTML pages are generated from `scripts/build.py` and `scripts/translations.json`; edit those files rather than the generated HTML. The site has no runtime framework or build step on GitHub Pages.

To update the site:

1. Edit the copy in `scripts/translations.json` or the layout in `scripts/build.py` and `assets/site.css`.
2. Run `python3 scripts/build.py` to regenerate all 28 pages and the sitemap.
3. Run `python3 -m http.server 8000` here to preview locally.
4. Run `python3 scripts/validate.py` before committing.

English lives at `/`. The other locales use `/zh-CN/`, `/ja/`, `/es/`, `/pt-BR/`, `/fr/`, and `/de/`. The language menu preserves the current page. Every localized page has its own canonical URL and `hreflang` links.

Ideas can be sent to `torres4koo@gmail.com` from the Submit page. Public [Feynman Lab Discussions](https://github.com/Feynman-Lab/discussions/discussions) remain available as an alternative.

from __future__ import annotations

import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "spec.yaml"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "dist" / "index.html"
ICON_CACHE = ROOT / "assets" / "icons"
ART_DIR = ROOT / "assets" / "art"
FONTS_DIR = ROOT / "assets" / "fonts"
DIST_ICONS = OUTPUT_PATH.parent / "icons"

USER_AGENT = "poe-endgame-poster/1.0"


def icon_filename(url: str) -> str:
    name = Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name
    stem, ext = name.rsplit(".", 1) if "." in name else (name, "png")
    stem = re.sub(r"_inventory_icon$", "", stem)
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return f"{slug}.{ext.lower()}"


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for _ in range(8):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                dest.write_bytes(response.read())
            return
        except urllib.error.HTTPError as err:
            if err.code == 429 or err.code >= 500:
                print(f"  HTTP {err.code}, waiting 60s: {url}")
                time.sleep(60)
                continue
            raise
    raise RuntimeError(f"kept failing after retries: {url}")


def localize_badge_icons(node) -> None:
    """Download remote badge icons into the cache and rewrite URLs to dist-relative paths."""
    if isinstance(node, dict):
        for badge in node.get("badges") or []:
            if isinstance(badge, dict) and str(badge.get("icon", "")).startswith("http"):
                filename = icon_filename(badge["icon"])
                cached = ICON_CACHE / filename
                if not cached.exists():
                    print(f"Downloading icon: {badge.get('label', filename)}")
                    fetch(badge["icon"], cached)
                shutil.copy2(cached, DIST_ICONS / filename)
                badge["icon"] = f"icons/{filename}"
        for value in node.values():
            localize_badge_icons(value)
    elif isinstance(node, list):
        for item in node:
            localize_badge_icons(item)


def collect_art_refs(node, found: set[str]) -> None:
    if isinstance(node, dict):
        for key in ("art", "headerArt"):
            value = node.get(key)
            if isinstance(value, str):
                found.add(value)
        for value in node.values():
            collect_art_refs(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_art_refs(item, found)


def main() -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    layout = spec["layout"]
    content = spec["content"]

    ICON_CACHE.mkdir(parents=True, exist_ok=True)
    DIST_ICONS.mkdir(parents=True, exist_ok=True)
    localize_badge_icons(content)

    art_refs: set[str] = set()
    collect_art_refs(content, art_refs)
    if art_refs:
        dist_art = OUTPUT_PATH.parent / "art"
        dist_art.mkdir(parents=True, exist_ok=True)
        for name in sorted(art_refs):
            source = ART_DIR / name
            if not source.is_file():
                raise FileNotFoundError(f"art file referenced in spec is missing: {source}")
            shutil.copy2(source, dist_art / name)

    if FONTS_DIR.is_dir():
        shutil.copytree(
            FONTS_DIR, OUTPUT_PATH.parent / "fonts",
            dirs_exist_ok=True, ignore=shutil.ignore_patterns("*Zone.Identifier"),
        )

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("__POSTER_WIDTH__", str(layout["poster_width"]))
    html = html.replace("__POSTER_MIN_HEIGHT__", str(layout["poster_min_height"]))
    html = html.replace("__CROWN_COLUMNS__", str(layout.get("crown_columns", 12)))
    html = html.replace("__GAME_VERSION__", str(layout["game_version"]))
    html = html.replace(
        "__POSTER_DATA__",
        json.dumps(content, ensure_ascii=False, indent=2),
    )

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

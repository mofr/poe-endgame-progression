from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "spec.yaml"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "dist" / "index.html"


def main() -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    layout = spec["layout"]
    content = spec["content"]

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("__POSTER_WIDTH__", str(layout["poster_width"]))
    html = html.replace("__POSTER_MIN_HEIGHT__", str(layout["poster_min_height"]))
    html = html.replace(
        "__POSTER_DATA__",
        json.dumps(content, ensure_ascii=False, indent=2),
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

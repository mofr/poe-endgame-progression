"""Render dist/index.html into print-ready output: a lossless PNG master
and a PDF wrapper with physical dimensions for the print shop.

Requires the print extras (once):
    python -m pip install playwright img2pdf
    python -m playwright install chromium

Usage:
    python print.py                # 3x scale (~256 dpi at 61 cm / 24 in width)
    python print.py --scale 4      # ~340 dpi at the same width
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_INDEX = ROOT / "dist" / "index.html"
OUT_DIR = ROOT / "print"


def render_png(scale: int, out_png: Path) -> tuple[int, int]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 2048, "height": 1400},
            device_scale_factor=scale,
        )
        page.goto(DIST_INDEX.as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(1000)
        css_width = page.evaluate("document.documentElement.scrollWidth")
        css_height = page.evaluate("document.documentElement.scrollHeight")
        page.screenshot(path=str(out_png), full_page=True)
        browser.close()
    return css_width * scale, css_height * scale


def wrap_pdf(png: Path, pdf: Path, dpi: int) -> None:
    import img2pdf
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None  # scale 4 exceeds Pillow's decompression-bomb limit
    layout = img2pdf.get_fixed_dpi_layout_fun((dpi, dpi))
    pdf.write_bytes(img2pdf.convert(str(png), layout_fun=layout))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, default=3,
                        help="device scale factor; 3 ≈ 256 dpi, 4 ≈ 340 dpi at 61 cm print width")
    args = parser.parse_args()

    if not DIST_INDEX.is_file():
        raise SystemExit("dist/index.html missing — run generate.py first")

    OUT_DIR.mkdir(exist_ok=True)
    out_png = OUT_DIR / "poster.png"
    out_pdf = OUT_DIR / "poster.pdf"

    width, height = render_png(args.scale, out_png)
    # 61 cm (24 in) print width is the sizing reference; the PDF just records
    # the physical size so the shop doesn't have to guess.
    dpi = round(width / 24)
    print(f"PNG master: {out_png} ({width} x {height} px)")

    wrap_pdf(out_png, out_pdf, dpi)
    inches_w, inches_h = width / dpi, height / dpi
    print(f"PDF: {out_pdf} ({inches_w:.1f} x {inches_h:.1f} in "
          f"/ {inches_w * 2.54:.0f} x {inches_h * 2.54:.0f} cm at {dpi} dpi)")


if __name__ == "__main__":
    main()

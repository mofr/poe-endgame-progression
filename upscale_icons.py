"""Real-ESRGAN the icons that the wiki only publishes at overlay resolution.

The influence / item symbols (Shaper, Elder, the four Conquerors, Synthesised,
Veiled) exist only as 27px stamps, which are ~3x undersampled once print.py
rasterises the poster at 3x. Plain resampling cannot recover them; a super-
resolution pass can. This rewrites the icons in assets/icons in place, so the
normal build stays dependency-free — run it only when a new small icon appears.

    python -m pip install torch spandrel pillow
    python upscale_icons.py --model /path/to/RealESRGAN_x4plus.pth
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ICON_CACHE = ROOT / "assets" / "icons"


def upscale(model, image, device):
    import numpy as np
    import torch
    from PIL import Image

    tensor = torch.from_numpy(np.asarray(image, dtype=np.float32) / 255.0)
    tensor = tensor.permute(2, 0, 1)[None].to(device)
    with torch.no_grad():
        out = model(tensor)
    arr = out[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()
    return Image.fromarray((arr * 255).round().astype("uint8"))


def main() -> None:
    import torch
    from PIL import Image
    from spandrel import ModelLoader

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Real-ESRGAN .pth weights")
    parser.add_argument("--min-size", type=int, default=40,
                        help="upscale icons narrower than this; the wiki's normal icons are 78px+")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ModelLoader().load_from_file(args.model).to(device).eval()
    print(f"{Path(args.model).name} on {device}, scale {model.scale}x")

    for path in sorted(ICON_CACHE.glob("*.png")):
        with Image.open(path) as img:
            icon = img.convert("RGBA")
        if icon.width >= args.min_size:
            continue
        rgb = upscale(model, icon.convert("RGB"), device)
        # alpha has no colour for the net to reason about, so send it through as grey
        alpha = upscale(model, Image.merge("RGB", [icon.split()[-1]] * 3), device).convert("L")
        out = rgb.convert("RGBA")
        out.putalpha(alpha)
        out.save(path)
        print(f"  {path.name}: {icon.width}px -> {out.width}px")


if __name__ == "__main__":
    main()

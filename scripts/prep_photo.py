"""
prep_photo.py — Prepare a source photo for ASCII art conversion.

Steps:
  1. Remove background with rembg (onnx-based, runs locally)
  2. Boost local contrast with CLAHE via OpenCV
  3. Composite onto pure white background
  4. Save as grayscale PNG → assets/images/source-prepped.png

Usage:
  python scripts/prep_photo.py path/to/your-photo.jpg
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import IMAGES_DIR, ensure_dirs


def prep_photo(source_path: str | Path) -> Path:
    import numpy as np
    import cv2
    from PIL import Image
    from rembg import remove

    source = Path(source_path).resolve()
    if not source.exists():
        print(f"ERROR: Source photo not found: {source}")
        sys.exit(1)

    ensure_dirs()
    output = IMAGES_DIR / "source-prepped.png"

    print(f"Loading {source} …")
    with open(source, "rb") as f:
        raw = f.read()

    # ── Step 1: Remove background ──────────────────────────────────────────
    print("Removing background (rembg) …")
    removed_bytes = remove(raw)  # returns PNG bytes with alpha
    from io import BytesIO
    img_rgba = Image.open(BytesIO(removed_bytes)).convert("RGBA")

    # ── Step 2: Composite onto white ───────────────────────────────────────
    white_bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    white_bg.paste(img_rgba, mask=img_rgba.split()[3])  # use alpha as mask
    img_rgb = white_bg.convert("RGB")

    # ── Step 3: CLAHE contrast enhancement ────────────────────────────────
    print("Applying CLAHE contrast enhancement …")
    img_cv = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2GRAY)
    clahe  = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    img_eq = clahe.apply(img_cv)

    # ── Step 4: Save ──────────────────────────────────────────────────────
    result = Image.fromarray(img_eq, mode="L")
    result.save(str(output))
    print(f"Wrote → {output}  ({output.stat().st_size:,} bytes)")
    return output


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <path-to-source-photo>")
        print("Example: python scripts/prep_photo.py assets/images/photo.jpg")
        sys.exit(1)
    prep_photo(sys.argv[1])


if __name__ == "__main__":
    main()

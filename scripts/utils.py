"""
utils.py — Shared helpers, config constants, and SVG building blocks
for the RATHAN005 GitHub profile art pipeline.
"""

from __future__ import annotations
import os
import textwrap
from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent   # d:/GitProfile/RATHAN005
SCRIPTS_DIR  = ROOT / "scripts"
DATA_DIR     = ROOT / "data"
ASSETS_DIR   = ROOT / "assets"
IMAGES_DIR   = ASSETS_DIR / "images"
ASCII_DIR    = ASSETS_DIR / "ascii"
CARDS_DIR    = ASSETS_DIR / "cards"
HEATMAP_DIR  = ASSETS_DIR / "heatmap"

# ── Profile config ────────────────────────────────────────────────────────────
USERNAME     = "RATHAN005"
DISPLAY_NAME = "Rathan K"
EMAIL        = "rathan14705@gmail.com"

# Neofetch card content (keep lines ≤ 42 chars for the SVG width)
INFO_LINES: list[tuple[str, str, str]] = [
    # (key_color, key, value)
    ("#39d353", "user",    f"{USERNAME}@github"),
    ("#555",    "─" * 22, ""),
    ("#a855f7", "role",    "Software Engineer"),
    ("#a855f7", "",        "Accessibility Engineer"),
    ("#6d28d9", "now",     "Accessibility Intern @ SQA"),
    ("#6d28d9", "",        "July 2026 – Present"),
    ("#4f46e5", "edu",     "B.E. CSE · Karpagam · 2027"),
    ("#7c3aed", "stack",   "React · Spring Boot · Node.js"),
    ("#7c3aed", "",        "Docker · Kubernetes · AWS"),
    ("#8b5cf6", "certs",   "AWS CCP · Oracle SQL/Java"),
    ("#8b5cf6", "",        "Cisco Net · Cisco Cyber"),
    ("#555",    "─" * 22, ""),
    ("#39d353", "open to", "Full Stack · DevOps"),
    ("#39d353", "",        "Accessibility · AI Tooling"),
    ("#555",    "─" * 22, ""),
    ("#a855f7", "email",   EMAIL),
]

# ── SVG helpers ───────────────────────────────────────────────────────────────
def svg_open(width: int, height: int, extra_attrs: str = "") -> str:
    """Return the opening <svg> tag."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'{extra_attrs}>'
    )


def svg_close() -> str:
    return "</svg>"


def embed_font(family: str = "JetBrains Mono") -> str:
    """Embed a Google Fonts @import for a monospace font inside a <style> block."""
    safe = family.replace(" ", "+")
    return (
        f'<style>'
        f'@import url("https://fonts.googleapis.com/css2?family={safe}:wght@400;600&display=swap");'
        f'</style>'
    )


def monospace_style(font_size: int = 13, fill: str = "#c9d1d9") -> str:
    """Return inline style string for monospace text."""
    return (
        f'font-family="JetBrains Mono, Consolas, monospace" '
        f'font-size="{font_size}" '
        f'fill="{fill}" '
        f'xml:space="preserve"'
    )


# ── Ensure output directories exist ──────────────────────────────────────────
def ensure_dirs() -> None:
    for d in (DATA_DIR, IMAGES_DIR, ASCII_DIR, CARDS_DIR, HEATMAP_DIR):
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print("Directories OK")
    print(f"Root: {ROOT}")

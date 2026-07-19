"""
make_info_card.py — Generate a neofetch-style animated info card SVG
for RATHAN005's GitHub profile README.

Each line fades + slides in with a stagger. Plays once, then freezes.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import ROOT, INFO_LINES, ensure_dirs

OUTPUT_SVG = ROOT / "info-card.svg"

# ── Layout ────────────────────────────────────────────────────────────────────
WIDTH        = 490
LINE_H       = 22          # px per line
PAD_X        = 20
PAD_TOP      = 52          # below title bar
PAD_BOTTOM   = 20
TITLE_H      = 38          # terminal title bar height
KEY_W        = 96          # fixed key column width
FONT         = "JetBrains Mono, Consolas, monospace"
FONT_SIZE    = 13

# Colours
BG           = "#0d1117"
TITLE_BG     = "#161b22"
TITLE_DOT_R  = "#ff5f57"
TITLE_DOT_Y  = "#febc2e"
TITLE_DOT_G  = "#28c840"
TITLE_TEXT   = "#8b949e"
VALUE_COLOR  = "#c9d1d9"
BORDER       = "#30363d"

HEIGHT = TITLE_H + PAD_TOP + len(INFO_LINES) * LINE_H + PAD_BOTTOM


def make_svg(static: bool = False) -> str:
    parts: list[str] = []

    # ── Opening tag ──
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    # ── Styles ──
    if static:
        anim_rules = ""
    else:
        stagger_rules = []
        for i in range(len(INFO_LINES)):
            delay = i * 60  # ms
            stagger_rules.append(
                f'.line-{i} {{ animation: fadeSlide 0.4s ease-out {delay}ms both; }}'
            )
        anim_rules = f"""
@keyframes fadeSlide {{
  from {{ opacity: 0; transform: translateX(-10px); }}
  to   {{ opacity: 1; transform: translateX(0); }}
}}
{chr(10).join(stagger_rules)}"""

    parts.append(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
{anim_rules}
</style>""")

    # ── Card background ──
    parts.append(
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )

    # ── Title bar ──
    parts.append(
        f'<rect width="{WIDTH}" height="{TITLE_H}" rx="10" fill="{TITLE_BG}"/>'
    )
    # Flat bottom of title bar
    parts.append(
        f'<rect y="{TITLE_H - 10}" width="{WIDTH}" height="10" fill="{TITLE_BG}"/>'
    )

    # Traffic-light dots
    for i, color in enumerate([TITLE_DOT_R, TITLE_DOT_Y, TITLE_DOT_G]):
        cx = 18 + i * 20
        cy = TITLE_H // 2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{color}"/>')

    # Title text
    parts.append(
        f'<text x="{WIDTH // 2}" y="{TITLE_H // 2 + 5}" '
        f'text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TITLE_TEXT}">'
        f'rathan@github — bash'
        f'</text>'
    )

    # ── Content lines ──
    for i, (key_color, key, value) in enumerate(INFO_LINES):
        y = TITLE_H + PAD_TOP + i * LINE_H
        cls = f'class="line-{i}"' if not static else ""

        # Separator lines (key is a bunch of dashes, no value)
        if key and all(c in "─-" for c in key):
            parts.append(
                f'<g {cls}>'
                f'<text x="{PAD_X}" y="{y}" '
                f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{key_color}">'
                f'{key}'
                f'</text>'
                f'</g>'
            )
            continue

        # First line of a block (key present)
        if key:
            parts.append(
                f'<g {cls}>'
                # Key
                f'<text x="{PAD_X}" y="{y}" '
                f'font-family="{FONT}" font-size="{FONT_SIZE}" '
                f'fill="{key_color}" font-weight="600">'
                f'{key}'
                f'</text>'
            )
            if value:
                parts.append(
                    f'<text x="{PAD_X + KEY_W}" y="{y}" '
                    f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{VALUE_COLOR}">'
                    f'<tspan fill="{key_color}">: </tspan>{value}'
                    f'</text>'
                )
            parts.append('</g>')
        else:
            # Continuation line (empty key, value wraps)
            parts.append(
                f'<g {cls}>'
                f'<text x="{PAD_X + KEY_W + 14}" y="{y}" '
                f'font-family="{FONT}" font-size="{FONT_SIZE}" fill="{VALUE_COLOR}">'
                f'{value}'
                f'</text>'
                f'</g>'
            )

    # ── Blinking cursor at the end ──
    if not static:
        cursor_y = TITLE_H + PAD_TOP + len(INFO_LINES) * LINE_H - 4
        parts.append(f"""<rect x="{PAD_X}" y="{cursor_y - 12}" width="8" height="14"
  fill="#a855f7">
  <animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>
</rect>""")

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    ensure_dirs()
    static = os.environ.get("STATIC", "0") == "1"
    svg = make_svg(static=static)
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Wrote → {OUTPUT_SVG}  ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()

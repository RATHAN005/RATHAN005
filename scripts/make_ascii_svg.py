"""
make_ascii_svg.py — Convert a prepped grayscale photo (or built-in fallback art)
into a self-typing monochrome ASCII SVG for RATHAN005's GitHub profile.

Animation: each row wipes left-to-right via a clipPath that expands,
with a small block "cursor" riding the right edge. Rows stagger top-to-bottom.
Plays once, then freezes.

Photo path: assets/images/source-prepped.png
Output:     rathan-ascii.svg

If the photo is missing, a stylised built-in avatar is used instead.
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import IMAGES_DIR, ROOT, ensure_dirs

OUTPUT_SVG  = ROOT / "rathan-ascii.svg"
PREPPED_IMG = IMAGES_DIR / "source-prepped.png"

# ── ASCII parameters ──────────────────────────────────────────────────────────
# Density ramp: index 0 = brightest (sparse), last = darkest (dense)
RAMP        = " .`':-=+*cso#%@"
CHAR_W      = 100    # character columns in the grid
CHAR_H      = 53     # character rows — matches ~2:1 cell aspect ratio

# ── SVG layout ────────────────────────────────────────────────────────────────
FONT_SIZE   = 7.5    # px — tight but readable
CHAR_PX_W   = 4.5    # px per character (monospace advance at font-size 7.5)
CHAR_PX_H   = 9.0    # px per row (line-height ~1.2×)
PAD_X       = 10
PAD_Y       = 14
SVG_W       = int(PAD_X * 2 + CHAR_W * CHAR_PX_W)   # ≈ 470
SVG_H       = int(PAD_Y * 2 + CHAR_H * CHAR_PX_H)   # ≈ 505
FONT        = "JetBrains Mono, Consolas, monospace"
FILL_COLOR  = "#b0bec5"   # monochrome light grey — clean on dark bg
BG_COLOR    = "#0d1117"
CURSOR_CLR  = "#a855f7"

# Animation timing
ROW_DELAY_MS   = 30    # stagger between rows
ROW_DUR_MS     = 380   # duration of each row's wipe
CURSOR_TRAIL   = 12    # px wide cursor block


# ── Built-in fallback art ─────────────────────────────────────────────────────
# A stylised "R" terminal avatar — used when no photo is present.
# 53 rows × 100 chars (padded to exactly CHAR_W with spaces).
_FALLBACK_ART_LINES = [
    "                                                                                                    ",
    "                                                                                                    ",
    "        .:::::::.    .:::::::.    :::::::::::   :::   :::       :::     ::::    :::                 ",
    "       :+:    :+:  :+:    :+:       :+:        :+:   :+:      :+:+:   :+:+:   :+:                 ",
    "      +:+    +:+  +:+    +:+       +:+        +:+   +:+     :+: +:+  +:+:+:  +:+                  ",
    "     +#++:++#:   +#+    +:+       +#+        +#+   +:+    +#+  +:+# +#+ +:+ +#+                   ",
    "    +#+    +#+  +#+    +#+       +#+        +#+   +#+   +#+#+#+#+#+ +#+  +#+#+#                    ",
    "   #+#    #+#  #+#    #+#       #+#        #+#   #+#   #+#    #+# #+#   #+#+#                     ",
    "  ###    ###   ########        ###         #######    ###    ### ###    ####                       ",
    "                                                                                                    ",
    "                                                                                                    ",
    "  ╔══════════════════════════════════════════════════════════════════════════════════════════╗      ",
    "  ║                                                                                          ║      ",
    "  ║   $ whoami                                                                               ║      ",
    "  ║   rathan — Software Engineer · Accessibility Engineer                                   ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ cat /etc/stack                                                                       ║      ",
    "  ║   React · Spring Boot · Node.js · Docker · Kubernetes · AWS · GitHub Actions            ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ cat /etc/role                                                                        ║      ",
    "  ║   Accessibility Intern @ SQA  |  B.E. CSE · Class of 2027                              ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ cat /etc/certs                                                                       ║      ",
    "  ║   AWS CCP · Oracle SQL/Java · Cisco Networking · Cisco Cybersecurity · NPTEL            ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ cat /etc/open_to                                                                     ║      ",
    "  ║   Full Stack  ·  DevOps / Cloud  ·  Accessibility  ·  AI Tooling                       ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ git log --oneline --projects                                                         ║      ",
    "  ║   abc1234  Kata-Sync — Chrome extension for dev workflow productivity                   ║      ",
    "  ║   def5678  DevSecOps Portal — JWT · RBAC · Vault · ArgoCD · Prometheus                 ║      ",
    "  ║   ghi9012  Staffbase — Spring Boot MVC · JWT · MySQL/PostgreSQL                        ║      ",
    "  ║   jkl3456  AI Chatbot on ESP32-C3 Mini — embedded C · Wi-Fi · REST AI                  ║      ",
    "  ║                                                                                          ║      ",
    "  ║   $ ping rathan14705@gmail.com                                                           ║      ",
    "  ║   PING success — I reply within 24h                                                     ║      ",
    "  ║                                                                                          ║      ",
    "  ╚══════════════════════════════════════════════════════════════════════════════════════════╝      ",
    "                                                                                                    ",
    "                                                                                                    ",
    "  ┌─────────────────────────────────────────────────────────────────────────────────────┐          ",
    "  │  WCAG 2.1  ·  NVDA  ·  Keyboard-only nav  ·  ARIA  ·  Assistive-tech auditing     │          ",
    "  └─────────────────────────────────────────────────────────────────────────────────────┘          ",
    "                                                                                                    ",
    "  ██████╗   ╦ ╦╦╦═╗╦  ╔╦╗                                                                         ",
    "  ██╔══██╗  ╠═╣║╠╣ ║  ║║║                                                                         ",
    "  ██████╔╝  ╩ ╩╩╩  ╩═╝╩ ╩                                                                         ",
    "  ██╔══██╗   Accessibility · DevOps · Full Stack · AI Tooling                                      ",
    "  ██████╔╝                                                                                          ",
    "  ╚═════╝    github.com/RATHAN005   ·   rathan14705@gmail.com                                      ",
    "                                                                                                    ",
    "                                                                                                    ",
    "                                                                                                    ",
]


def _pad_line(line: str, width: int = CHAR_W) -> str:
    """Pad / truncate a line to exactly `width` characters."""
    return line[:width].ljust(width)


def load_image_art() -> list[str] | None:
    """Try to load and convert the prepped photo to ASCII rows. Returns None if unavailable."""
    if not PREPPED_IMG.exists():
        return None
    try:
        from PIL import Image
        img = Image.open(PREPPED_IMG).convert("L")
        img = img.resize((CHAR_W, CHAR_H), Image.LANCZOS)

        rows: list[str] = []
        pixels = img.load()
        for row in range(CHAR_H):
            line = ""
            for col in range(CHAR_W):
                brightness = pixels[col, row]       # 0=black, 255=white
                idx = int(brightness / 255 * (len(RAMP) - 1))
                idx = len(RAMP) - 1 - idx           # invert: bright → sparse
                line += RAMP[idx]
            rows.append(line)
        return rows
    except Exception as e:
        print(f"WARNING: Could not load image ({e}). Using fallback art.")
        return None


def make_svg(rows: list[str]) -> str:
    parts: list[str] = []
    n_rows = len(rows)
    total_anim_ms = n_rows * ROW_DELAY_MS + ROW_DUR_MS

    # ── Header ──
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">'
    )

    # ── Styles ──
    # Each row has an animation class; cursor fades in/out at end of row wipe
    parts.append(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&amp;display=swap');
@keyframes wipeIn {{
  from {{ clip-path: inset(0 100% 0 0); }}
  to   {{ clip-path: inset(0 0% 0 0); }}
}}
</style>""")

    # ── Background ──
    parts.append(
        f'<rect width="{SVG_W}" height="{SVG_H}" fill="{BG_COLOR}"/>'
    )

    # ── Rows ──
    # We use SVG <clipPath> + animation to wipe each row left-to-right.
    # Each row gets its own clipPath and animated <rect> inside it.
    defs_parts: list[str] = []
    text_parts: list[str] = []

    for ri, line in enumerate(rows):
        clip_id = f"cr{ri}"
        delay   = ri * ROW_DELAY_MS
        dur     = ROW_DUR_MS
        x       = PAD_X
        y       = PAD_Y + ri * CHAR_PX_H + FONT_SIZE   # text baseline

        # clipPath with an animated rect expanding left→right
        defs_parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{x}" y="{y - FONT_SIZE}" '
            f'height="{CHAR_PX_H + 1}">'
            f'<animate attributeName="width" '
            f'from="0" to="{SVG_W}" '
            f'dur="{dur}ms" begin="{delay}ms" '
            f'fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )

        # Escape XML special chars in the art line
        safe = (line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

        text_parts.append(
            f'<text clip-path="url(#{clip_id})" '
            f'x="{x}" y="{y}" '
            f'font-family="{FONT}" font-size="{FONT_SIZE}" '
            f'fill="{FILL_COLOR}" xml:space="preserve">'
            f'{safe}'
            f'</text>'
        )

    parts.append(f'<defs>{"".join(defs_parts)}</defs>')
    parts.extend(text_parts)

    # ── Blinking cursor that appears after the last row finishes ──
    last_row_end_ms = (n_rows - 1) * ROW_DELAY_MS + ROW_DUR_MS
    cursor_y = PAD_Y + n_rows * CHAR_PX_H - 2
    parts.append(
        f'<rect x="{PAD_X}" y="{cursor_y - int(FONT_SIZE)}" '
        f'width="6" height="{int(FONT_SIZE) + 1}" '
        f'fill="{CURSOR_CLR}" opacity="0">'
        f'<animate attributeName="opacity" '
        f'values="0;1;0" dur="1.1s" '
        f'begin="{last_row_end_ms}ms" repeatCount="indefinite"/>'
        f'</rect>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    ensure_dirs()
    rows = load_image_art()
    if rows is None:
        print("No prepped photo found — using built-in stylised avatar art.")
        rows = [_pad_line(l) for l in _FALLBACK_ART_LINES]
    else:
        print(f"Loaded image art: {len(rows)} rows × {CHAR_W} cols")
        rows = [_pad_line(r) for r in rows]

    svg = make_svg(rows)
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Wrote → {OUTPUT_SVG}  ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()

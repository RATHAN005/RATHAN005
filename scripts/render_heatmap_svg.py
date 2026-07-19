"""
render_heatmap_svg.py — Read data/contributions.json and render an animated
53-week × 7-day contribution heatmap SVG.

Animation: each column (week) slides in with a slight diagonal stagger,
plays once on page load, then freezes. No looping, no external deps.
"""

from __future__ import annotations
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import DATA_DIR, ROOT, USERNAME, ensure_dirs

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_SVG = ROOT / "contrib-heatmap.svg"

# ── Layout constants ──────────────────────────────────────────────────────────
CELL        = 12      # cell size (px)
GAP         = 3       # gap between cells (px)
STEP        = CELL + GAP    # 15 px per column/row
COLS        = 53
ROWS        = 7
PAD_LEFT    = 32      # space for weekday labels
PAD_TOP     = 36      # space for month labels
PAD_BOTTOM  = 56      # space for stats footer
PAD_RIGHT   = 20
LEGEND_H    = 28      # legend strip height

GRID_W = COLS * STEP - GAP
GRID_H = ROWS * STEP - GAP

SVG_W = PAD_LEFT + GRID_W + PAD_RIGHT
SVG_H = PAD_TOP  + GRID_H + PAD_BOTTOM

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#0d1117"
TEXT_DIM  = "#8b949e"
TEXT_MED  = "#c9d1d9"
BORDER    = "#21262d"

# level 0-5 (0 = no contributions, 5 = max neon)
PALETTE = [
    "#161b22",   # 0 – empty
    "#0e4429",   # 1
    "#006d32",   # 2
    "#26a641",   # 3
    "#39d353",   # 4
    "#69f0a0",   # 5 – neon top
]

DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


# ── Helpers ───────────────────────────────────────────────────────────────────
def level_to_color(level: int) -> str:
    idx = max(0, min(level, len(PALETTE) - 1))
    return PALETTE[idx]


def count_to_level(count: int) -> int:
    """Map raw count to a 0-5 display level."""
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    if count <= 15:
        return 4
    return 5


def build_week_grid(days: list[dict]) -> list[list[dict | None]]:
    """
    Return a list of 53 columns, each a list of 7 day-dicts (or None for padding).
    Column 0 = oldest week, Column 52 = most recent.
    Row 0 = Sunday, row 6 = Saturday.
    """
    # Index by date string for O(1) lookup
    by_date: dict[str, dict] = {d["date"]: d for d in days}

    # Find the range: last 53 weeks ending on the most recent Saturday
    today = date.today()
    # Go to the most recent Saturday (weekday 5)
    end = today + timedelta(days=(5 - today.weekday() - 1) % 7)
    start = end - timedelta(weeks=COLS) + timedelta(days=1)
    # Align start to Sunday
    start = start - timedelta(days=(start.weekday() + 1) % 7)

    grid: list[list[dict | None]] = []
    cursor = start
    for _ in range(COLS):
        col: list[dict | None] = []
        for row in range(ROWS):
            key = cursor.isoformat()
            col.append(by_date.get(key))
            cursor += timedelta(days=1)
        grid.append(col)
    return grid


def month_labels(grid: list[list[dict | None]]) -> list[tuple[int, str]]:
    """
    Return (col_index, month_name) for the first column of each new month.
    """
    labels: list[tuple[int, str]] = []
    prev_month = None
    for ci, col in enumerate(grid):
        # Use the first non-None date in the column
        for cell in col:
            if cell:
                m = cell["date"][5:7]
                if m != prev_month:
                    mn = datetime.strptime(cell["date"], "%Y-%m-%d").strftime("%b")
                    labels.append((ci, mn))
                    prev_month = m
                break
    return labels


# ── SVG generation ────────────────────────────────────────────────────────────
FONT = "JetBrains Mono, Consolas, monospace"

def make_svg(grid: list[list[dict | None]], stats: dict) -> str:
    parts: list[str] = []

    # ── Header ──
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">'
    )

    # ── Styles ──
    # Each column gets its own CSS animation class for the diagonal stagger.
    # Animation: slide in from above + fade in, then freeze (forwards fill).
    anim_css_parts = []
    for ci in range(COLS):
        delay = ci * 18   # ms — diagonal stagger across 53 columns ≈ ~0.95 s total
        anim_css_parts.append(
            f'.col-{ci} {{ animation: slideIn 0.35s ease-out {delay}ms both; }}'
        )

    parts.append(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&amp;display=swap');
* {{ font-family: '{FONT}'; }}
@keyframes slideIn {{
  from {{ opacity: 0; transform: translateY(-8px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
{chr(10).join(anim_css_parts)}
</style>""")

    # ── Background ──
    parts.append(
        f'<rect width="{SVG_W}" height="{SVG_H}" rx="12" fill="{BG}"/>'
    )

    # ── Month labels ──
    for ci, label in month_labels(grid):
        x = PAD_LEFT + ci * STEP
        parts.append(
            f'<text x="{x}" y="{PAD_TOP - 8}" '
            f'font-family="{FONT}" font-size="10" fill="{TEXT_DIM}">{label}</text>'
        )

    # ── Weekday labels (Mon / Wed / Fri only) ──
    for ri, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = PAD_TOP + ri * STEP + CELL - 1
        parts.append(
            f'<text x="{PAD_LEFT - 6}" y="{y}" '
            f'text-anchor="end" font-family="{FONT}" font-size="9" fill="{TEXT_DIM}">{name}</text>'
        )

    # ── Cell grid ──
    for ci, col in enumerate(grid):
        # Wrap the column's cells in a <g> with the animation class
        parts.append(f'<g class="col-{ci}">')
        for ri, cell in enumerate(col):
            x = PAD_LEFT + ci * STEP
            y = PAD_TOP  + ri * STEP
            if cell is None:
                color = PALETTE[0]
                count = 0
                day_str = ""
            else:
                count   = cell["count"]
                color   = level_to_color(count_to_level(count))
                day_str = cell["date"]

            tip = f"{count} contribution{'s' if count != 1 else ''} on {day_str}" if day_str else ""
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}">'
                + (f'<title>{tip}</title>' if tip else '')
                + '</rect>'
            )
        parts.append('</g>')

    # ── Stats footer ──
    total  = stats.get("total_contributions", 0)
    streak = stats.get("current_streak", 0)
    longest= stats.get("longest_streak", 0)
    best   = stats.get("best_day", {})
    best_c = best.get("count", 0)
    best_d = best.get("date", "")

    footer_y = PAD_TOP + GRID_H + 18
    parts.append(
        f'<text x="{PAD_LEFT}" y="{footer_y}" '
        f'font-family="{FONT}" font-size="11" fill="{TEXT_MED}">'
        f'{total:,} contributions in the last year'
        f'</text>'
    )

    # Second stat row
    stat2_y = footer_y + 16
    parts.append(
        f'<text x="{PAD_LEFT}" y="{stat2_y}" '
        f'font-family="{FONT}" font-size="10" fill="{TEXT_DIM}">'
        f'Streak: {streak} days  •  Longest: {longest}  •  Best day: {best_c} ({best_d})'
        f'</text>'
    )

    # ── Legend ──
    legend_x_start = SVG_W - PAD_RIGHT - (len(PALETTE) * (CELL + 2)) - 40
    legend_y       = stat2_y - 2
    parts.append(
        f'<text x="{legend_x_start - 6}" y="{legend_y + CELL - 1}" '
        f'text-anchor="end" font-family="{FONT}" font-size="9" fill="{TEXT_DIM}">Less</text>'
    )
    for li, color in enumerate(PALETTE):
        lx = legend_x_start + li * (CELL + 2)
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    end_x = legend_x_start + len(PALETTE) * (CELL + 2) + 4
    parts.append(
        f'<text x="{end_x}" y="{legend_y + CELL - 1}" '
        f'font-family="{FONT}" font-size="9" fill="{TEXT_DIM}">More</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    ensure_dirs()
    contrib_file = DATA_DIR / "contributions.json"

    if not contrib_file.exists():
        print(f"ERROR: {contrib_file} not found. Run fetch_contributions.py first.")
        sys.exit(1)

    data  = json.loads(contrib_file.read_text())
    days  = data.get("days", [])
    stats = data.get("stats", {})

    print(f"Loaded {len(days)} days of contribution data.")

    grid = build_week_grid(days)
    svg  = make_svg(grid, stats)

    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Wrote → {OUTPUT_SVG}  ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()

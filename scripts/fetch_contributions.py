"""
fetch_contributions.py — Scrape the public GitHub contribution calendar
for RATHAN005 and write data/contributions.json.

No API token required. GitHub serves the contribution HTML at:
  https://github.com/users/<username>/contributions
"""

from __future__ import annotations
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Make sure sibling imports work when run as a script
sys.path.insert(0, str(Path(__file__).parent))
from utils import USERNAME, DATA_DIR, ensure_dirs


CONTRIB_URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_FILE = DATA_DIR / "contributions.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_html() -> str:
    print(f"Fetching {CONTRIB_URL} …")
    resp = requests.get(CONTRIB_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    """
    Return a list of dicts:
      { "date": "YYYY-MM-DD", "count": int, "level": int (0-4) }
    sorted oldest → newest.

    GitHub (2024+) renders each day as:
      <td data-date="2025-07-19" data-level="0" id="contribution-day-component-0-0" ...>
    and the tooltip as:
      <tool-tip for="contribution-day-component-0-0">3 contributions on July 19th.</tool-tip>
    """
    soup = BeautifulSoup(html, "html.parser")

    # ── Build a tooltip lookup: cell-id → tooltip text ────────────────────────
    tooltip_by_id: dict[str, str] = {}
    for tip in soup.find_all("tool-tip", attrs={"for": True}):
        cell_id = tip.get("for", "")
        tooltip_by_id[cell_id] = tip.get_text(strip=True)

    # ── Find all day cells ────────────────────────────────────────────────────
    cells = soup.find_all("td", attrs={"data-date": True})
    if not cells:
        cells = soup.find_all("rect", attrs={"data-date": True})

    days: list[dict] = []
    for cell in cells:
        day_str = cell.get("data-date", "")
        level   = int(cell.get("data-level", 0))
        cell_id = cell.get("id", "")

        # Try tooltip text first (most accurate), then fallback to aria-label/title
        label = (
            tooltip_by_id.get(cell_id, "")
            or cell.get("aria-label", "")
            or cell.get("title", "")
        )
        count = _parse_count_from_label(label)

        # If tooltip was missing / said "No contributions", trust data-level for
        # a rough count (level gives 0/1-2/3-5/6-9/10+ buckets) — better than 0.
        if count == 0 and level > 0:
            count = [0, 1, 3, 6, 10, 15][min(level, 5)]

        if day_str:
            days.append({
                "date":  day_str,
                "count": count,
                "level": level,
            })

    days.sort(key=lambda d: d["date"])
    return days


def _parse_count_from_label(label: str) -> int:
    """Extract integer contribution count from an aria-label string."""
    if not label:
        return 0
    parts = label.strip().split()
    if parts and parts[0].isdigit():
        return int(parts[0])
    # "No contributions" → 0
    return 0


def compute_stats(days: list[dict]) -> dict:
    """Derive streak, best day, totals from the day list."""
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    # Best single day
    best = max(days, key=lambda d: d["count"])

    # Current streak (counting back from today / the last day with data)
    today = date.today().isoformat()
    streak = 0
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            streak += 1
        else:
            break

    # Longest streak ever
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    # Monthly totals (last 12 months)
    monthly: dict[str, int] = defaultdict(int)
    for d in days:
        month_key = d["date"][:7]  # "YYYY-MM"
        monthly[month_key] += d["count"]

    return {
        "total_contributions": total,
        "current_streak":      streak,
        "longest_streak":      longest,
        "best_day":            {"date": best["date"], "count": best["count"]},
        "monthly_totals":      dict(sorted(monthly.items())[-13:]),
    }


def main() -> None:
    ensure_dirs()
    html  = fetch_html()
    days  = parse_days(html)

    if not days:
        print("WARNING: No contribution day cells found. GitHub may have changed its markup.")
        print("Writing empty contributions file.")
        days = []

    stats = compute_stats(days)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username":     USERNAME,
        "stats":        stats,
        "days":         days,
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(days)} days → {OUTPUT_FILE}")
    if stats:
        print(f"  Total : {stats['total_contributions']}")
        print(f"  Streak: {stats['current_streak']} days (longest {stats['longest_streak']})")
        print(f"  Best  : {stats['best_day']['count']} on {stats['best_day']['date']}")


if __name__ == "__main__":
    main()

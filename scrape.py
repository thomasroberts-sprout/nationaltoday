#!/usr/bin/env python3
"""Scrape today's holidays from nationaltoday.com and write data.json + index.html."""

from __future__ import annotations

import html
import json
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://nationaltoday.com/today/"
USER_AGENT = "MyHolidayBot/1.0 (personal project; local+github-actions)"
ROOT = Path(__file__).resolve().parent


def scrape_holidays() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    today = date.today()
    weekday = today.strftime("%a").upper()
    month_day = today.strftime("%b %d").upper().replace(" 0", " ")

    holidays: list[dict] = []
    for card in soup.select(".card-holiday"):
        link = card.select_one("a.card-holiday-image-wrapper") or card.select_one("a[href]")
        title_el = card.select_one(".card-holiday-title")
        img = card.select_one("img")

        month_el = card.select_one(".ntdb-holiday-day")
        day_el = card.select_one(".ntdb-holiday-date")
        if month_el and day_el:
            month_day = f"{month_el.get_text(strip=True)} {day_el.get_text(strip=True)}".upper()

        name = title_el.get_text(strip=True) if title_el else None
        href = link.get("href") if link else None
        image = None
        if img:
            image = img.get("src") or img.get("data-src")

        if name and href:
            holidays.append(
                {
                    "name": name,
                    "url": href,
                    "image": image,
                    "weekday": weekday,
                    "month_day": month_day,
                }
            )

    return holidays


def render_html(holidays: list[dict], scraped_at: str, day_label: str) -> str:
    data_json = json.dumps(holidays)
    max_count = max(len(holidays), 1)
    options = []
    for n in range(1, max_count + 1):
        selected = " selected" if n == min(5, max_count) else ""
        options.append(f'<option value="{n}"{selected}>{n}</option>')
    options_html = "\n          ".join(options)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Today's Holidays — {html.escape(day_label)}</title>
  <style>
    :root {{
      --red: #e31c23;
      --teal: #00a8c5;
      --ink: #222;
      --muted: #666;
      --page: #fff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      min-height: 100vh;
    }}
    header {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 2rem 1.25rem 0.75rem;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
    }}
    .header-text h1 {{
      margin: 0 0 0.25rem;
      font-size: 1.75rem;
      font-weight: 700;
    }}
    .header-text p {{
      margin: 0;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .count-picker {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 0.35rem;
      flex-shrink: 0;
    }}
    .count-picker label {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .count-picker select {{
      font: inherit;
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--ink);
      border: 2px solid #ddd;
      border-radius: 8px;
      padding: 0.4rem 0.65rem;
      background: #fff;
      cursor: pointer;
      min-width: 4.5rem;
    }}
    .count-picker select:focus {{
      outline: 2px solid var(--teal);
      outline-offset: 2px;
    }}
    .featured-wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 0.5rem 1.25rem 1.5rem;
    }}
    .featured {{
      position: relative;
      border-radius: 18px;
      overflow: hidden;
      min-height: 280px;
      background: #333;
    }}
    .featured-slide {{
      display: none;
      position: relative;
      min-height: 280px;
      padding: 1.25rem 1.5rem 3.5rem;
      background-size: cover;
      background-position: center;
      text-decoration: none;
      color: #fff;
    }}
    .featured-slide::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0.42);
    }}
    .featured-slide.is-active {{ display: block; }}
    .featured-label {{
      position: relative;
      z-index: 1;
      display: inline-block;
      background: #fff;
      color: var(--red);
      font-size: 0.7rem;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: 0.35rem 0.55rem;
      border-radius: 4px;
    }}
    .featured-date {{
      position: absolute;
      z-index: 1;
      top: 0;
      right: 1.25rem;
      background: var(--red);
      color: #fff;
      padding: 0.45rem 0.55rem 0.5rem;
      line-height: 1.05;
      text-align: center;
      min-width: 3.4rem;
    }}
    .featured-date .dow,
    .date-badge .dow {{
      display: block;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .featured-date .md,
    .date-badge .md {{
      display: block;
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: 0.02em;
      margin-top: 0.1rem;
    }}
    .featured-title {{
      position: absolute;
      z-index: 1;
      left: 1.5rem;
      right: 1.5rem;
      top: 50%;
      transform: translateY(-50%);
      text-align: center;
      font-size: clamp(1.4rem, 4vw, 2.4rem);
      font-weight: 800;
      letter-spacing: 0.02em;
      line-height: 1.15;
      text-shadow: 0 2px 12px rgba(0,0,0,0.35);
    }}
    .featured-nav {{
      position: absolute;
      z-index: 2;
      bottom: 1rem;
      width: 2rem;
      height: 2rem;
      border: none;
      border-radius: 50%;
      background: #fff;
      color: var(--teal);
      font-size: 1.35rem;
      line-height: 1;
      cursor: pointer;
      display: none;
      place-items: center;
      padding: 0 0 0.1rem;
    }}
    .featured-nav.is-visible {{ display: grid; }}
    .featured-nav.prev {{ left: 1.25rem; }}
    .featured-nav.next {{ right: 1.25rem; }}
    .featured-nav:hover {{ background: #f3f3f3; }}
    .grid {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 0.25rem 1.25rem 0.5rem;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem 1.25rem;
    }}
    @media (max-width: 520px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .featured {{ min-height: 220px; }}
      .featured-slide {{ min-height: 220px; }}
      header {{ flex-direction: column; }}
      .count-picker {{ align-items: flex-start; }}
    }}
    .card {{
      display: block;
      min-width: 0;
    }}
    .card-media {{
      position: relative;
      display: block;
      width: 100%;
      aspect-ratio: 1;
      overflow: hidden;
      background: #ddd;
      text-decoration: none;
      color: #fff;
    }}
    .card-media img,
    .placeholder {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.25s ease;
    }}
    .card-media:hover img {{
      transform: scale(1.04);
    }}
    .date-badge {{
      position: absolute;
      z-index: 2;
      top: 0;
      left: 0;
      background: var(--red);
      color: #fff;
      padding: 0.45rem 0.55rem 0.5rem;
      line-height: 1.05;
      text-align: center;
      min-width: 3.4rem;
    }}
    .card-title {{
      position: absolute;
      z-index: 2;
      left: 0;
      right: 0;
      bottom: 0;
      margin: 0;
      padding: 2.5rem 0.85rem 0.9rem;
      font-size: 1.05rem;
      font-weight: 700;
      line-height: 1.25;
      color: #fff;
      background: linear-gradient(transparent, rgba(0,0,0,0.72));
      opacity: 0;
      transform: translateY(6px);
      transition: opacity 0.2s ease, transform 0.2s ease;
      pointer-events: none;
    }}
    .card-media:hover .card-title,
    .card-media:focus-visible .card-title {{
      opacity: 1;
      transform: translateY(0);
    }}
    .see-more-wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 0.5rem 1.25rem 2rem;
      display: flex;
      justify-content: flex-end;
    }}
    .see-more {{
      display: inline-block;
      border: 2px solid var(--teal);
      color: var(--teal);
      background: transparent;
      padding: 0.55rem 1rem;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-decoration: none;
      text-transform: uppercase;
    }}
    .see-more:hover {{
      background: var(--teal);
      color: #fff;
    }}
    footer {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 0 1.25rem 2.5rem;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    footer a {{ color: var(--teal); }}
    .empty {{ grid-column: 1 / -1; color: var(--muted); }}
    .featured-wrap.is-hidden,
    .grid.is-hidden {{ display: none; }}
  </style>
</head>
<body>
  <header>
    <div class="header-text">
      <h1>Today's Holidays</h1>
      <p>{html.escape(day_label)} · updated {html.escape(scraped_at)}</p>
    </div>
    <div class="count-picker">
      <label for="count">Show</label>
      <select id="count" aria-label="How many holidays to show">
          {options_html}
      </select>
    </div>
  </header>
  <section class="featured-wrap" id="featured-wrap" aria-label="Featured today">
    <div class="featured" id="featured">
      <button class="featured-nav prev" type="button" aria-label="Previous">&#8249;</button>
      <button class="featured-nav next" type="button" aria-label="Next">&#8250;</button>
    </div>
  </section>
  <main class="grid" id="grid"></main>
  <div class="see-more-wrap">
    <a class="see-more" href="https://nationaltoday.com/today/" target="_blank" rel="noopener noreferrer">See More &gt;</a>
  </div>
  <footer>
    Data sourced from
    <a href="https://nationaltoday.com/today/" target="_blank" rel="noopener noreferrer">National Today</a>
    (names, images, and links only — not article text).
  </footer>
  <script>
    (function () {{
      var ALL = {data_json};
      var DEFAULT = 5;
      var KEY = "holidayCount";
      var featuredRoot = document.getElementById("featured");
      var featuredWrap = document.getElementById("featured-wrap");
      var grid = document.getElementById("grid");
      var select = document.getElementById("count");
      var prevBtn = featuredRoot.querySelector(".prev");
      var nextBtn = featuredRoot.querySelector(".next");
      var featuredIndex = 0;
      var visible = [];

      function esc(s) {{
        return String(s == null ? "" : s)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;");
      }}

      function getCount() {{
        var n = parseInt(select.value, 10);
        if (!n || n < 1) n = Math.min(DEFAULT, ALL.length);
        return Math.min(n, ALL.length);
      }}

      function renderFeatured(item) {{
        var existing = featuredRoot.querySelector(".featured-slide");
        if (existing) existing.remove();
        if (!item) {{
          featuredWrap.classList.add("is-hidden");
          return;
        }}
        featuredWrap.classList.remove("is-hidden");
        var a = document.createElement("a");
        a.className = "featured-slide is-active";
        a.href = item.url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.style.backgroundImage = item.image ? "url('" + esc(item.image) + "')" : "";
        a.innerHTML =
          '<span class="featured-label">Featured</span>' +
          '<span class="featured-date"><span class="dow">' + esc(item.weekday) +
          '</span><span class="md">' + esc(item.month_day) + '</span></span>' +
          '<span class="featured-title">' + esc((item.name || "").toUpperCase()) + '</span>';
        featuredRoot.insertBefore(a, prevBtn);
        var showNav = visible.length > 1;
        prevBtn.classList.toggle("is-visible", showNav);
        nextBtn.classList.toggle("is-visible", showNav);
      }}

      function renderCards(items) {{
        if (!items.length) {{
          grid.innerHTML = "";
          grid.classList.add("is-hidden");
          return;
        }}
        grid.classList.remove("is-hidden");
        grid.innerHTML = items.map(function (h) {{
          return (
            '<article class="card">' +
              '<a class="card-media" href="' + esc(h.url) + '" target="_blank" rel="noopener noreferrer">' +
                (h.image
                  ? '<img src="' + esc(h.image) + '" alt="' + esc(h.name) + '" loading="lazy" width="400" height="400">'
                  : '<div class="placeholder"></div>') +
                '<div class="date-badge"><span class="dow">' + esc(h.weekday) +
                '</span><span class="md">' + esc(h.month_day) + '</span></div>' +
                '<span class="card-title">' + esc(h.name) + '</span>' +
              '</a>' +
            '</article>'
          );
        }}).join("");
      }}

      function apply() {{
        var count = getCount();
        visible = ALL.slice(0, count);
        if (featuredIndex >= visible.length) featuredIndex = 0;
        var featured = visible[featuredIndex];
        var cards = visible.filter(function (_, i) {{ return i !== featuredIndex; }});
        renderFeatured(featured);
        renderCards(cards);
        try {{ localStorage.setItem(KEY, String(count)); }} catch (e) {{}}
      }}

      var saved = null;
      try {{ saved = parseInt(localStorage.getItem(KEY), 10); }} catch (e) {{}}
      if (saved && saved >= 1 && saved <= ALL.length) {{
        select.value = String(saved);
      }} else {{
        select.value = String(Math.min(DEFAULT, ALL.length));
      }}

      select.addEventListener("change", function () {{
        featuredIndex = 0;
        apply();
      }});
      prevBtn.addEventListener("click", function (e) {{
        e.preventDefault();
        if (visible.length < 2) return;
        featuredIndex = (featuredIndex - 1 + visible.length) % visible.length;
        apply();
      }});
      nextBtn.addEventListener("click", function (e) {{
        e.preventDefault();
        if (visible.length < 2) return;
        featuredIndex = (featuredIndex + 1) % visible.length;
        apply();
      }});

      apply();
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    holidays = scrape_holidays()
    now = datetime.now(timezone.utc)
    scraped_at = now.strftime("%Y-%m-%d %H:%M UTC")
    day_label = date.today().strftime("%A, %B %d, %Y").replace(" 0", " ")

    payload = {
        "scraped_at": scraped_at,
        "source": URL,
        "count": len(holidays),
        "holidays": holidays,
    }

    (ROOT / "data.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (ROOT / "index.html").write_text(
        render_html(holidays, scraped_at, day_label), encoding="utf-8"
    )
    print(f"Wrote {len(holidays)} holidays → data.json + index.html")


if __name__ == "__main__":
    main()

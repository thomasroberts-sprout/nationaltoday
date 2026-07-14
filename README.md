# Today's Holidays

Scrapes [nationaltoday.com/today](https://nationaltoday.com/today/) for holiday **name**, **image**, and **link**, then renders a simple card grid.

## Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.org/simple/ -r requirements.txt
python scrape.py
open index.html
```

## Free hosting

1. Push this repo to GitHub
2. Settings → Pages → Deploy from branch: `main` / `/ (root)`
3. Actions runs daily at 06:00 UTC (or use **Run workflow**)

Stack: Python scraper → `index.html` → GitHub Pages (all free)

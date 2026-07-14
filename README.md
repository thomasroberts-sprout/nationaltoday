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

Stack: Python scraper → `index.html` → GitHub Pages (all free)

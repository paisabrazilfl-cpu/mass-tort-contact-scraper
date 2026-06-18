# Mass Tort Contact Scraper

A Python utility that reads search terms from `search_terms.txt`, queries Google Custom Search API (if configured) or falls back to Bing web search, parses results with BeautifulSoup, and outputs a JSON array compatible with SCOUT.

## Usage

```bash
python scrape_contacts.py
```

## Files
- `scrape_contacts.py` – main script.
- `search_terms.txt` – list of search queries (one per line).
- `README.md` – this file.

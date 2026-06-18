import json
import os
import sys
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

# Optional: Google Custom Search API credentials via environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')

# Optional: Bing Search API key via environment variable (not used in fallback)
BING_API_KEY = os.getenv('BING_API_KEY')

def google_custom_search(query: str, num_results: int = 10) -> List[Dict]:
    """Query Google Custom Search API if credentials are set.
    Returns a list of dicts with keys: title, url, snippet.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return []
    endpoint = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CX,
        'q': query,
        'num': num_results,
    }
    resp = requests.get(endpoint, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get('items', []):
        results.append({
            'title': item.get('title'),
            'url': item.get('link'),
            'snippet': item.get('snippet'),
            'source': 'google'
        })
    return results

def bing_web_search(query: str, num_results: int = 10) -> List[Dict]:
    """Fallback web scrape of Bing search results.
    Returns a list of dicts with keys: title, url, snippet.
    """
    # Simple GET request to Bing search page
    url = 'https://www.bing.com/search'
    params = {'q': query, 'count': num_results}
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MassTortScraper/1.0)'
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    # Bing result blocks have <li class="b_algo">
    for li in soup.select('li.b_algo')[:num_results]:
        a_tag = li.find('a')
        title = a_tag.get_text(strip=True) if a_tag else ''
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
        snippet_tag = li.find('p')
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
        results.append({
            'title': title,
            'url': link,
            'snippet': snippet,
            'source': 'bing'
        })
    return results

def search_term(term: str) -> List[Dict]:
    # Try Google first
    results = google_custom_search(term)
    if results:
        return results
    # Fallback to Bing scraping
    return bing_web_search(term)

def load_search_terms(file_path: str) -> List[str]:
    if not os.path.isfile(file_path):
        print(f'Error: search terms file not found: {file_path}', file=sys.stderr)
        sys.exit(1)
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    terms_file = 'search_terms.txt'
    terms = load_search_terms(terms_file)
    all_results = []
    for term in terms:
        try:
            res = search_term(term)
            for r in res:
                # Attach original query for traceability
                r['query'] = term
                all_results.append(r)
            # Be polite to servers
            time.sleep(1)
        except Exception as e:
            print(f'Error searching "{term}": {e}', file=sys.stderr)
    # Output JSON array compatible with SCOUT (assumed generic)
    print(json.dumps(all_results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

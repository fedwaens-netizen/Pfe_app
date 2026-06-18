import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY       = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY  = os.getenv("UNSPLASH_ACCESS_KEY")

# URLs à rejeter — problématiques ou trop génériques
BAD_URL_MARKERS = [
    'wikimedia', 'wikipedia', 'upload.wiki',
    '.svg', 'carte', 'map', 'locator', 'blason', 'coat_of_arms',
    'flag', 'drapeau', 'logo', 'portrait', 'symbol', 'emblem', 'insignia', 'seal'
]

FALLBACK_IMG = "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&h=600&fit=crop&q=80"


def _is_bad_url(url: str) -> bool:
    """Returns True if the URL is likely a low-quality or broken image."""
    if not url:
        return True
    low = url.lower()
    return any(m in low for m in BAD_URL_MARKERS)


def fetch_unsplash_image(query: str) -> str | None:
    """Fetch a landscape image from Unsplash."""
    if not UNSPLASH_ACCESS_KEY:
        return None
    url = (
        f"https://api.unsplash.com/search/photos"
        f"?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
    )
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            results = r.json().get("results", [])
            for result in results:
                img_url = result["urls"].get("regular") or result["urls"].get("full")
                if img_url and not _is_bad_url(img_url):
                    return img_url
    except Exception as e:
        print(f"[image_service] Unsplash error: {e}")
    return None


def fetch_pexels_image(query: str) -> str | None:
    """Fetch a high-quality image from Pexels."""
    if not PEXELS_API_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for photo in photos:
                img_url = photo["src"].get("large") or photo["src"].get("medium")
                if img_url and not _is_bad_url(img_url):
                    return img_url
    except Exception as e:
        print(f"[image_service] Pexels error: {e}")
    return None


def fetch_wikipedia_image(city_name: str) -> str | None:
    """Fetch the main image from Wikipedia, rejecting bad images (maps, logos...)."""
    headers = {'User-Agent': 'MoroccoTourismApp/1.0'}

    for lang in ['en', 'fr']:
        api_url = (
            f"https://{lang}.wikipedia.org/w/api.php"
            f"?action=query&prop=pageimages&format=json&piprop=original"
            f"&titles={urllib.parse.quote(city_name)}"
        )
        try:
            r = requests.get(api_url, headers=headers, timeout=5)
            if r.status_code == 200:
                pages = r.json().get('query', {}).get('pages', {})
                for page_data in pages.values():
                    img_url = page_data.get('original', {}).get('source', '')
                    if img_url and not _is_bad_url(img_url):
                        return img_url
        except Exception:
            continue

    return None


from db.database import SessionLocal
from db import crud


def get_best_destination_image(destination_name: str, fallback_query: str = None) -> str:
    """
    Fetch the best available image for a destination.
    Priority: Unsplash → Pexels → Wikipedia (filtered) → generic fallback.
    Always caches results to avoid repeated API calls.
    Never stores Wikimedia or bad URLs.
    """
    search_query = f"{destination_name} Morocco"

    db = SessionLocal()
    try:
        # 1. Check cache first
        cached_url = crud.get_cached_image(db, search_query)
        if cached_url and not _is_bad_url(cached_url):
            return cached_url

        img_url = None

        # 2. Unsplash (best quality)
        img_url = fetch_unsplash_image(search_query)

        # 3. Pexels fallback
        if not img_url:
            img_url = fetch_pexels_image(search_query)

        # 4. Wikipedia (filtered, last resort)
        if not img_url:
            wiki_url = fetch_wikipedia_image(destination_name)
            if wiki_url and not _is_bad_url(wiki_url):
                img_url = wiki_url

        # 5. Try fallback_query (e.g. region name)
        if not img_url and fallback_query:
            fallback_search = f"{fallback_query} Morocco"
            cached_fallback = crud.get_cached_image(db, fallback_search)
            if cached_fallback and not _is_bad_url(cached_fallback):
                return cached_fallback
            img_url = fetch_unsplash_image(fallback_search) or fetch_pexels_image(fallback_search)

        # 6. Ultimate fallback — always return something valid
        if not img_url:
            img_url = FALLBACK_IMG

        # Cache the result
        if img_url and not _is_bad_url(img_url):
            crud.cache_image(db, search_query, img_url)

        return img_url

    finally:
        db.close()

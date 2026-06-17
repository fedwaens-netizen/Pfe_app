import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def fetch_unsplash_image(query: str):
    """Fetch high-quality image from Unsplash."""
    if not UNSPLASH_ACCESS_KEY:
        return None
    url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                # Pick the first image as it's the most relevant
                return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash API error: {e}")
    return None

def fetch_pexels_image(query: str):
    """Fetch high-quality image from Pexels."""
    if not PEXELS_API_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("photos"):
                # Pick the first image as it's the most relevant
                return data["photos"][0]["src"]["large"]
    except Exception as e:
        print(f"Pexels API error: {e}")
    return None

def fetch_wikipedia_image(city_name: str):
    """Fetch official page image from Wikipedia."""
    headers = {'User-Agent': 'MoroccoTourismApp/1.0'}
    
    # Try French wiki first
    url_fr = f"https://fr.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(city_name)}"
    try:
        r = requests.get(url_fr, headers=headers, timeout=5)
        if r.status_code == 200:
            pages = r.json().get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'original' in page_data:
                    return page_data['original']['source']
    except Exception:
        pass
        
    # Try English wiki
    url_en = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(city_name)}"
    try:
        r = requests.get(url_en, headers=headers, timeout=5)
        if r.status_code == 200:
            pages = r.json().get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'original' in page_data:
                    return page_data['original']['source']
    except Exception:
        pass
        
    return None

from db.database import SessionLocal
from db import crud

def get_best_destination_image(destination_name: str, fallback_query: str = None):
    """
    Tries to find the highest quality image for a destination.
    Order of preference: Unsplash -> Pexels -> Wikipedia.
    """
    search_query = f"{destination_name} Morocco"
    
    db = SessionLocal()
    try:
        # Check cache first
        cached_url = crud.get_cached_image(db, search_query)
        if cached_url:
            return cached_url
            
        img_url = None
        # 1. Try Unsplash (if key provided)
        img_url = fetch_unsplash_image(search_query)
        
        # 2. Try Pexels (if key provided)
        if not img_url:
            img_url = fetch_pexels_image(search_query)
            
        # 3. Fallback to free Wikipedia API
        if not img_url:
            wiki_url = fetch_wikipedia_image(destination_name)
            blocked_words = ['.svg', 'carte', 'map', 'locator', 'blason', 'coat_of_arms', 'flag', 'drapeau', 'logo', 'portrait', 'symbol', 'emblem', 'insignia', 'seal']
            if wiki_url and not any(blocked in wiki_url.lower() for blocked in blocked_words):
                img_url = wiki_url
                
        # 4. If all fails, use the fallback query (e.g. general city name)
        if not img_url and fallback_query:
            fallback_search = f"{fallback_query} Morocco"
            cached_fallback = crud.get_cached_image(db, fallback_search)
            if cached_fallback:
                return cached_fallback
            img_url = fetch_unsplash_image(fallback_search)
            if img_url:
                search_query = fallback_search # Cache under fallback query too
                
        if img_url:
            crud.cache_image(db, search_query, img_url)
            return img_url
            
    finally:
        db.close()
        
    return None

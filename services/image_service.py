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
                import random
                # Pick a random image from top 5 to avoid duplicates
                return random.choice(data["results"])["urls"]["regular"]
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
                import random
                return random.choice(data["photos"])["src"]["large"]
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

def get_best_destination_image(destination_name: str, fallback_query: str = None):
    """
    Tries to find the highest quality image for a destination.
    Order of preference: Unsplash -> Pexels -> Wikipedia.
    """
    search_query = f"{destination_name} Morocco"
    
    # 1. Try Unsplash (if key provided)
    img_url = fetch_unsplash_image(search_query)
    if img_url:
        return img_url
        
    # 2. Try Pexels (if key provided)
    img_url = fetch_pexels_image(search_query)
    if img_url:
        return img_url
        
    # 3. Fallback to free Wikipedia API
    img_url = fetch_wikipedia_image(destination_name)
    if img_url and not any(blocked in img_url.lower() for blocked in ['.svg', 'carte', 'map', 'locator', 'blason', 'coat_of_arms']):
        return img_url
            
    # 4. If all fails, use the fallback query (e.g. general city name)
    if fallback_query:
        img_url = fetch_unsplash_image(f"{fallback_query} Morocco")
        if img_url:
            return img_url
            
    return None

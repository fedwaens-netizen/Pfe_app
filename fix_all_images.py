# -*- coding: utf-8 -*-
"""
Script de correction globale des images.
"""
import os
import sys
import io
import requests
import urllib.parse
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal, Destination, DestinationImage, ImageCache

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXELS_KEY   = os.getenv("PEXELS_API_KEY")

FALLBACK_IMG = "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&h=600&fit=crop&q=80"

BAD_URL_MARKERS = [
    'wikimedia', 'wikipedia', 'upload.wiki',
    '.svg', 'carte', 'map', 'locator', 'blason', 'coat_of_arms',
    'flag', 'drapeau', 'logo', 'portrait', 'symbol', 'emblem'
]

def is_bad_url(url):
    if not url:
        return True
    low = url.lower()
    return any(m in low for m in BAD_URL_MARKERS)

def fetch_unsplash(query):
    if not UNSPLASH_KEY:
        return None
    url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
    try:
        r = requests.get(url, headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}, timeout=6)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["urls"]["regular"]
    except Exception as e:
        print(f"  [Unsplash error] {e}")
    return None

def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3"
    try:
        r = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=6)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large"]
    except Exception as e:
        print(f"  [Pexels error] {e}")
    return None

def get_best_image(name):
    query = f"{name} Morocco"
    img = fetch_unsplash(query)
    if not img:
        img = fetch_pexels(query)
    return img or FALLBACK_IMG

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Etape 1: Vidage du cache ImageCache...")
        count = db.query(ImageCache).count()
        db.query(ImageCache).delete()
        db.commit()
        print(f"  {count} entrees de cache supprimees.")

        print("\nEtape 2: Nettoyage des images cassees...")
        all_imgs = db.query(DestinationImage).all()
        bad_imgs = [img for img in all_imgs if is_bad_url(img.url)]
        for img in bad_imgs:
            db.delete(img)
        db.commit()
        print(f"  {len(bad_imgs)} images cassees supprimees sur {len(all_imgs)}.")

        print("\nEtape 3: Re-fetch des images pour les destinations sans image...")
        destinations = db.query(Destination).all()
        
        # Refresh après suppression
        db.expire_all()
        no_image = [d for d in destinations if not d.images]
        print(f"  {len(no_image)} destinations sans image sur {len(destinations)} totales.")

        for i, dest in enumerate(no_image, 1):
            print(f"  [{i}/{len(no_image)}] {dest.name}...")
            img_url = get_best_image(dest.name)
            
            new_img = DestinationImage(url=img_url, destination_id=dest.id)
            db.add(new_img)
            
            cache_entry = ImageCache(query=f"{dest.name} Morocco", url=img_url)
            db.add(cache_entry)
            
            try:
                db.commit()
                print(f"    OK: {img_url[:80]}")
            except Exception as ex:
                db.rollback()
                print(f"    ERREUR: {ex}")

        print("\n" + "=" * 60)
        print("Termine!")
        
        total_with_imgs = db.query(Destination).join(DestinationImage).distinct().count()
        total_dests = db.query(Destination).count()
        print(f"  Destinations avec images : {total_with_imgs}/{total_dests}")

    finally:
        db.close()

if __name__ == "__main__":
    main()

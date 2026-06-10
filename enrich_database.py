import json
import urllib.request
import urllib.parse
import time
import os

def get_wikipedia_image(query, size=800):
    """
    Search Wikipedia for the query and return the main image URL.
    Uses better heuristics to prefer landscapes/monuments over infrastructure.
    """
    # Prefer landscape/tourism keywords to avoid train stations/admin buildings
    search_query = f"{query} landscape tourism"
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_query)}&utf8=&format=json"
    
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'MoroGo-PFE/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            search_results = data.get('query', {}).get('search', [])
            
            if not search_results:
                # Try French Wikipedia as fallback if English fails
                search_url = f"https://fr.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query + ' paysage')}&utf8=&format=json"
                req = urllib.request.Request(search_url, headers={'User-Agent': 'MoroGo-PFE/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    search_results = data.get('query', {}).get('search', [])
                
            if not search_results:
                return None
                
            title = search_results[0]['title']
            
            # Get the main image
            page_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize={size}"
            # Fallback to general query if title seems too specific (like "Station")
            if "station" in title.lower() or "railway" in title.lower() or "gare" in title.lower():
                 if len(search_results) > 1:
                     title = search_results[1]['title']
            
            req2 = urllib.request.Request(page_url, headers={'User-Agent': 'MoroGo-PFE/1.0'})
            with urllib.request.urlopen(req2) as response2:
                data2 = json.loads(response2.read().decode())
                pages = data2.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if 'thumbnail' in page_info:
                        return page_info['thumbnail']['source']
    except Exception as e:
        pass
    return None

def main():
    data_path = 'morocco_data.json'
    print(f"Reading {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Enriching {len(data)} destinations. This may take a moment...")
    
    # We will prioritize cities with no images or generic ones
    for i, city in enumerate(data):
        name = city['name']
        print(f"[{i+1}/{len(data)}] {name}...")
        
        # 1. City main image
        if not city.get('images') or 'unsplash' in city['images'][0]:
            img = get_wikipedia_image(f"{name} Morocco")
            if img:
                city['images'] = [img]
                print(f"  + New city image found.")
        
        # 2. Places images
        for place in city.get('places', []):
            if not place.get('image') or place['image'] == "":
                p_img = get_wikipedia_image(f"{place['name']} {name}")
                if p_img:
                    place['image'] = p_img
                    print(f"    - Image for {place['name']} found.")
        
        # Short sleep to respect Wikipedia API
        time.sleep(0.05)
        
        # Periodic save
        if (i+1) % 10 == 0:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    # Final save
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("\nGlobal enrichment completed successfully.")

if __name__ == "__main__":
    main()

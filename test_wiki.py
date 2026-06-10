import requests
import urllib.parse

def get_wiki_image(city_name):
    headers = {'User-Agent': 'MoroccoTourismApp/1.0 (test@test.com)'}
    try:
        url = f"https://fr.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(city_name)}"
        r = requests.get(url, headers=headers)
        pages = r.json().get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'original' in page_data:
                return page_data['original']['source']
                
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(city_name)}"
        r = requests.get(url, headers=headers)
        pages = r.json().get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'original' in page_data:
                return page_data['original']['source']
    except Exception as e:
        return f"Error: {e}"
    return None

print("Casablanca:", get_wiki_image("Casablanca"))
print("Chefchaouen:", get_wiki_image("Chefchaouen"))
print("Ighzrane:", get_wiki_image("Ighzrane"))
print("Imlili:", get_wiki_image("Imlili"))

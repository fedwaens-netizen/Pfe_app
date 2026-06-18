import json
import os

locales_dir = r"c:\Users\Lenovo\Documents\BTS-2026\Projet-Fin-Etude\frontend-old\src\locales"
langs = ['fr', 'en', 'ar']

new_keys = {
    'fr': {
        'home': {
            'categories': {
                'all': 'Tout',
                'nature': 'Montagne & Nature',
                'beaches': 'Plage & Océan',
                'desert': 'Désert & Oasis',
                'history': 'Villes & Histoire',
                'culture': 'Villages & Culture'
            }
        }
    },
    'en': {
        'home': {
            'categories': {
                'all': 'All',
                'nature': 'Mountains & Nature',
                'beaches': 'Beach & Ocean',
                'desert': 'Desert & Oasis',
                'history': 'Cities & History',
                'culture': 'Villages & Culture'
            }
        }
    },
    'ar': {
        'home': {
            'categories': {
                'all': 'الكل',
                'nature': 'الجبال والطبيعة',
                'beaches': 'الشاطئ والمحيط',
                'desert': 'الصحراء والواحات',
                'history': 'المدن والتاريخ',
                'culture': 'القرى والثقافة'
            }
        }
    }
}

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

for lang in langs:
    file_path = os.path.join(locales_dir, lang, "translation.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data = deep_update(data, new_keys[lang])
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("Translation files updated successfully.")

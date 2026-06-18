import json
import os

locales_dir = r"c:\Users\Lenovo\Documents\BTS-2026\Projet-Fin-Etude\frontend-old\src\locales"
langs = ['fr', 'en', 'ar']

new_keys = {
    'fr': {
        'home': {
            'exploreOther': "Explorez d'autres destinations",
            'dynamicTrending': "Tendances Actuelles (Par les utilisateurs)",
            'pagination': {
                'prev': "Précédent",
                'next': "Suivant",
                'page': "Page {current} / {total}"
            },
            'noDestinationFound': "Aucune destination trouvée pour"
        }
    },
    'en': {
        'home': {
            'exploreOther': "Explore other destinations",
            'dynamicTrending': "Current Trends (By users)",
            'pagination': {
                'prev': "Previous",
                'next': "Next",
                'page': "Page {current} / {total}"
            },
            'noDestinationFound': "No destination found for"
        }
    },
    'ar': {
        'home': {
            'exploreOther': "استكشف وجهات أخرى",
            'dynamicTrending': "الاتجاهات الحالية (من قبل المستخدمين)",
            'pagination': {
                'prev': "السابق",
                'next': "التالي",
                'page': "صفحة {current} / {total}"
            },
            'noDestinationFound': "لم يتم العثور على وجهة لـ"
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

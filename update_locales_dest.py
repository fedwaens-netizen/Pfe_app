import json
import os

locales_dir = r"c:\Users\Lenovo\Documents\BTS-2026\Projet-Fin-Etude\frontend-old\src\locales"
langs = ['fr', 'en', 'ar']

new_keys = {
    'fr': {
        'destination': {
            'loading': 'Chargement de votre destination...',
            'errorTitle': 'Oups !',
            'notFound': 'Destination introuvable.',
            'backToHome': "Retour à l'accueil",
            'back': 'Retour',
            'discover': 'Découvrez {name}',
            'gallery': 'Photos & Galerie',
            'map': 'Carte Interactive',
            'places': 'Lieux Incontournables',
            'emptyCategory': 'Aucun lieu trouvé pour cette catégorie.',
            'seeAllPlaces': 'Voir tous les lieux',
            'readyTitle': 'Prêt à organiser votre voyage ?',
            'readySubtitle': 'Découvrez les meilleurs hébergements à {name}',
            'bookHotel': 'Réserver un hôtel',
            'filters': {
                'all': 'Tout',
                'nature': 'Nature',
                'history': 'Histoire',
                'food': 'Gastronomie',
                'museums': 'Musées'
            }
        }
    },
    'en': {
        'destination': {
            'loading': 'Loading your destination...',
            'errorTitle': 'Oops!',
            'notFound': 'Destination not found.',
            'backToHome': 'Back to home',
            'back': 'Back',
            'discover': 'Discover {name}',
            'gallery': 'Photos & Gallery',
            'map': 'Interactive Map',
            'places': 'Must-See Places',
            'emptyCategory': 'No places found for this category.',
            'seeAllPlaces': 'See all places',
            'readyTitle': 'Ready to plan your trip?',
            'readySubtitle': 'Discover the best accommodations in {name}',
            'bookHotel': 'Book a hotel',
            'filters': {
                'all': 'All',
                'nature': 'Nature',
                'history': 'History',
                'food': 'Food & Drink',
                'museums': 'Museums'
            }
        }
    },
    'ar': {
        'destination': {
            'loading': 'جاري تحميل وجهتك...',
            'errorTitle': 'عفوا!',
            'notFound': 'الوجهة غير موجودة.',
            'backToHome': 'العودة للصفحة الرئيسية',
            'back': 'رجوع',
            'discover': 'اكتشف {name}',
            'gallery': 'الصور والمعرض',
            'map': 'خريطة تفاعلية',
            'places': 'أماكن لا تفوت',
            'emptyCategory': 'لم يتم العثور على أماكن لهذه الفئة.',
            'seeAllPlaces': 'رؤية جميع الأماكن',
            'readyTitle': 'مستعد لتنظيم رحلتك؟',
            'readySubtitle': 'اكتشف أفضل أماكن الإقامة في {name}',
            'bookHotel': 'حجز فندق',
            'filters': {
                'all': 'الكل',
                'nature': 'الطبيعة',
                'history': 'التاريخ',
                'food': 'طعام وشراب',
                'museums': 'المتاحف'
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

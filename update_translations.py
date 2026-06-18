import json
import os

locales_dir = r"c:\Users\Lenovo\Documents\BTS-2026\Projet-Fin-Etude\frontend-old\src\locales"

new_keys = {
    "fr": {
        "hotels": {
            "title": "Découvrez des hôtels d'exception",
            "subtitle": "Séjournez dans les meilleurs établissements du Maroc.",
            "searchDestination": "Destination",
            "placeholder": "Ex: Marrakech, Agadir...",
            "checkIn": "Arrivée",
            "checkOut": "Départ",
            "searchBtn": "Rechercher",
            "searching": "Recherche...",
            "error": "Erreur lors de la recherche d'hôtels.",
            "filterStars": "Filtrer par étoiles",
            "all": "Toutes",
            "maxPrice": "Prix max",
            "perNight": "/nuit",
            "bookBtn": "Réserver",
            "downloadReceipt": "Télécharger le Reçu",
            "noFilters": "Aucun hôtel ne correspond à vos critères de filtrage.",
            "noDest": "Entrez une destination pour voir les hôtels disponibles.",
            "success": "Réservation réussie et payée ! Un SMS de confirmation a été envoyé.",
            "back": "Retour"
        },
        "taxis": {
            "title": "Réservez votre trajet",
            "subtitle": "Trouvez un taxi ou VTC fiable partout au Maroc.",
            "pickup": "Lieu de départ",
            "dropoff": "Lieu d'arrivée",
            "date": "Date du trajet",
            "passengers": "Passagers",
            "searchBtn": "Rechercher",
            "searching": "Recherche...",
            "error": "Erreur lors de la recherche de taxis.",
            "filterType": "Filtrer par type",
            "all": "Tous",
            "maxPrice": "Prix max",
            "capacity": "places",
            "bookBtn": "Réserver",
            "downloadReceipt": "Télécharger le Reçu",
            "noFilters": "Aucun taxi ne correspond à vos critères.",
            "noDest": "Entrez un départ et une arrivée.",
            "success": "Réservation réussie et payée ! Le chauffeur vous contactera.",
            "back": "Retour",
            "types": {
                "Standard": "Standard",
                "Confort": "Confort",
                "Van": "Van",
                "Luxe": "Luxe"
            }
        },
        "bookings": {
            "title": "Mes Réservations",
            "subtitle": "Gérez vos séjours et trajets prévus.",
            "hotels": "Hôtels",
            "taxis": "Taxis",
            "noHotels": "Aucune réservation d'hôtel.",
            "noTaxis": "Aucune réservation de taxi.",
            "status": "Statut",
            "dates": "Dates",
            "guests": "Personnes",
            "route": "Trajet",
            "date": "Date",
            "cancel": "Annuler",
            "downloadReceipt": "Télécharger le Reçu"
        }
    },
    "en": {
        "hotels": {
            "title": "Discover Exceptional Hotels",
            "subtitle": "Stay in the best establishments in Morocco.",
            "searchDestination": "Destination",
            "placeholder": "Ex: Marrakech, Agadir...",
            "checkIn": "Check-in",
            "checkOut": "Check-out",
            "searchBtn": "Search",
            "searching": "Searching...",
            "error": "Error while searching for hotels.",
            "filterStars": "Filter by stars",
            "all": "All",
            "maxPrice": "Max price",
            "perNight": "/night",
            "bookBtn": "Book",
            "downloadReceipt": "Download Receipt",
            "noFilters": "No hotels match your filter criteria.",
            "noDest": "Enter a destination to view available hotels.",
            "success": "Booking successful and paid! A confirmation SMS has been sent.",
            "back": "Back"
        },
        "taxis": {
            "title": "Book your ride",
            "subtitle": "Find a reliable taxi or private driver anywhere in Morocco.",
            "pickup": "Pickup Location",
            "dropoff": "Dropoff Location",
            "date": "Ride Date",
            "passengers": "Passengers",
            "searchBtn": "Search",
            "searching": "Searching...",
            "error": "Error while searching for taxis.",
            "filterType": "Filter by type",
            "all": "All",
            "maxPrice": "Max price",
            "capacity": "seats",
            "bookBtn": "Book",
            "downloadReceipt": "Download Receipt",
            "noFilters": "No taxis match your criteria.",
            "noDest": "Enter a pickup and dropoff location.",
            "success": "Booking successful and paid! The driver will contact you.",
            "back": "Back",
            "types": {
                "Standard": "Standard",
                "Confort": "Comfort",
                "Van": "Van",
                "Luxe": "Luxury"
            }
        },
        "bookings": {
            "title": "My Bookings",
            "subtitle": "Manage your upcoming stays and rides.",
            "hotels": "Hotels",
            "taxis": "Taxis",
            "noHotels": "No hotel bookings.",
            "noTaxis": "No taxi bookings.",
            "status": "Status",
            "dates": "Dates",
            "guests": "Guests",
            "route": "Route",
            "date": "Date",
            "cancel": "Cancel",
            "downloadReceipt": "Download Receipt"
        }
    },
    "ar": {
        "hotels": {
            "title": "اكتشف فنادق استثنائية",
            "subtitle": "أقم في أفضل المؤسسات في المغرب.",
            "searchDestination": "الوجهة",
            "placeholder": "مثال: مراكش، أكادير...",
            "checkIn": "تاريخ الوصول",
            "checkOut": "تاريخ المغادرة",
            "searchBtn": "بحث",
            "searching": "جاري البحث...",
            "error": "حدث خطأ أثناء البحث عن الفنادق.",
            "filterStars": "تصفية حسب النجوم",
            "all": "الكل",
            "maxPrice": "الحد الأقصى للسعر",
            "perNight": "/ليلة",
            "bookBtn": "احجز",
            "downloadReceipt": "تنزيل الإيصال",
            "noFilters": "لا توجد فنادق تطابق معايير التصفية الخاصة بك.",
            "noDest": "أدخل وجهة لعرض الفنادق المتاحة.",
            "success": "تم الحجز والدفع بنجاح! تم إرسال رسالة نصية قصيرة للتأكيد.",
            "back": "رجوع"
        },
        "taxis": {
            "title": "احجز رحلتك",
            "subtitle": "اعثر على سيارة أجرة أو سائق خاص موثوق في أي مكان في المغرب.",
            "pickup": "مكان الانطلاق",
            "dropoff": "مكان الوصول",
            "date": "تاريخ الرحلة",
            "passengers": "الركاب",
            "searchBtn": "بحث",
            "searching": "جاري البحث...",
            "error": "حدث خطأ أثناء البحث عن سيارات الأجرة.",
            "filterType": "تصفية حسب النوع",
            "all": "الكل",
            "maxPrice": "الحد الأقصى للسعر",
            "capacity": "مقاعد",
            "bookBtn": "احجز",
            "downloadReceipt": "تنزيل الإيصال",
            "noFilters": "لا توجد سيارات أجرة تطابق معاييرك.",
            "noDest": "أدخل مكان الانطلاق والوصول.",
            "success": "تم الحجز والدفع بنجاح! سيتصل بك السائق.",
            "back": "رجوع",
            "types": {
                "Standard": "عادي",
                "Confort": "مريح",
                "Van": "فان",
                "Luxe": "فاخر"
            }
        },
        "bookings": {
            "title": "حجوزاتي",
            "subtitle": "إدارة إقاماتك ورحلاتك القادمة.",
            "hotels": "الفنادق",
            "taxis": "سيارات الأجرة",
            "noHotels": "لا توجد حجوزات فنادق.",
            "noTaxis": "لا توجد حجوزات سيارات أجرة.",
            "status": "الحالة",
            "dates": "التواريخ",
            "guests": "الأشخاص",
            "route": "المسار",
            "date": "التاريخ",
            "cancel": "إلغاء",
            "downloadReceipt": "تنزيل الإيصال"
        }
    }
}

for lang, keys in new_keys.items():
    file_path = os.path.join(locales_dir, lang, "translation.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.update(keys)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {lang}/translation.json")
    else:
        print(f"File {file_path} not found.")

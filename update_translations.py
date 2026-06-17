import json
import os

locales_dir = r"c:\Users\Lenovo\Documents\BTS-2026\Projet-Fin-Etude\frontend\src\locales"

new_keys = {
    "fr": {
        "admin": {
            "title": "Tableau de Bord Administrateur",
            "subtitle": "Aperçu en temps réel des activités de la plateforme.",
            "users": "Utilisateurs",
            "revenue": "Chiffre d'Affaires",
            "hotelBookings": "Réservations Hôtels",
            "taxiBookings": "Réservations Taxis",
            "trends": "Tendances des 7 Derniers Jours",
            "revenueDistribution": "Répartition des Revenus",
            "recentActivity": "Activités Récentes",
            "tableType": "Type",
            "tableDetails": "Détails",
            "tableUser": "Utilisateur",
            "tableDate": "Date",
            "tableAmount": "Montant",
            "tableStatus": "Statut",
            "noActivity": "Aucune activité récente."
        }
    },
    "en": {
        "admin": {
            "title": "Admin Dashboard",
            "subtitle": "Real-time overview of platform activities.",
            "users": "Users",
            "revenue": "Total Revenue",
            "hotelBookings": "Hotel Bookings",
            "taxiBookings": "Taxi Bookings",
            "trends": "Last 7 Days Trends",
            "revenueDistribution": "Revenue Distribution",
            "recentActivity": "Recent Activities",
            "tableType": "Type",
            "tableDetails": "Details",
            "tableUser": "User",
            "tableDate": "Date",
            "tableAmount": "Amount",
            "tableStatus": "Status",
            "noActivity": "No recent activity."
        }
    },
    "ar": {
        "admin": {
            "title": "لوحة تحكم المسؤول",
            "subtitle": "نظرة عامة في الوقت الفعلي على أنشطة المنصة.",
            "users": "المستخدمين",
            "revenue": "إجمالي الإيرادات",
            "hotelBookings": "حجوزات الفنادق",
            "taxiBookings": "حجوزات سيارات الأجرة",
            "trends": "اتجاهات آخر 7 أيام",
            "revenueDistribution": "توزيع الإيرادات",
            "recentActivity": "الأنشطة الأخيرة",
            "tableType": "النوع",
            "tableDetails": "التفاصيل",
            "tableUser": "المستخدم",
            "tableDate": "التاريخ",
            "tableAmount": "المبلغ",
            "tableStatus": "الحالة",
            "noActivity": "لا يوجد نشاط أخير."
        }
    }
}

for lang in ["fr", "en", "ar"]:
    path = os.path.join(locales_dir, lang, "translation.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Merge new keys. Keep existing admin link in nav under nav.admin if possible. Wait, the old "admin" key was a string inside "nav"
        if "adminPage" not in data:
            data["adminPage"] = new_keys[lang]["admin"]
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print("Translations updated!")

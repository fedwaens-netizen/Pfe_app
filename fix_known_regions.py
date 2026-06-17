import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:Kxsd2882@localhost:5432/touristes_db')

city_region_mapping = {
    # Ouest
    'Azemmour': 'Casablanca-Settat',
    'Sidi Bennour': 'Casablanca-Settat',
    'Youssoufia': 'Marrakech-Safi',
    'Chellah': 'Rabat-Salé-Kénitra',
    'Bouznika': 'Casablanca-Settat',
    'Skhirat': 'Rabat-Salé-Kénitra',
    'Salé': 'Rabat-Salé-Kénitra',
    'Temara': 'Rabat-Salé-Kénitra',
    
    # Sud-Ouest
    'Mirleft': 'Guelmim-Oued Noun',
    'Imouzzer Ida Outanane': 'Souss-Massa',
    'Tafraoute': 'Souss-Massa',
    'Taghazout': 'Souss-Massa',
    'Tamraght': 'Souss-Massa',
    'Tata': 'Souss-Massa',
    'Ait Melloul': 'Souss-Massa',
    'Inezgane': 'Souss-Massa',
    'Aoulouz': 'Souss-Massa',
    'Taliouine': 'Souss-Massa',
    'Laâyoune': 'Laâyoune-Sakia El Hamra',
    'Boujdour': 'Laâyoune-Sakia El Hamra',
    'Tarfaya': 'Laâyoune-Sakia El Hamra',
    'Bir Gandouz': 'Dakhla-Oued Ed-Dahab',
    'Assa': 'Guelmim-Oued Noun',
    
    # Sud-Est
    'Zagora': 'Drâa-Tafilalet',
    'Skoura': 'Drâa-Tafilalet',
    'Rissani': 'Drâa-Tafilalet',
    "M'hamid El Ghizlane": 'Drâa-Tafilalet',
    'Boumalne Dadès': 'Drâa-Tafilalet',
    'Aït Benhaddou': 'Drâa-Tafilalet',
    'Agdz': 'Drâa-Tafilalet',
    'Kelaat Mgouna': 'Drâa-Tafilalet',
    'Goulmima': 'Drâa-Tafilalet',
    'Tinjdad': 'Drâa-Tafilalet',
    'Alnif': 'Drâa-Tafilalet',
    'Hassilabiad': 'Drâa-Tafilalet',
    'Ksar Ait Arbi': 'Drâa-Tafilalet',
    'Nekob': 'Drâa-Tafilalet',
    'Tamegroute': 'Drâa-Tafilalet',
    'Ait Saoun': 'Drâa-Tafilalet',
    
    # Centre
    'Boujniba': 'Béni Mellal-Khénifra',
    "M'rirt": 'Béni Mellal-Khénifra',
    'Itzer': 'Béni Mellal-Khénifra',
    'Aghbala': 'Béni Mellal-Khénifra',
    'El Ksiba': 'Béni Mellal-Khénifra',
    'Zaouiat Cheikh': 'Béni Mellal-Khénifra',
    
    # Centre-Est
    'Missour': 'Fès-Meknès',
    'Outat El Haj': 'Fès-Meknès',
    
    # Oriental
    'Nador': "l'Oriental",
    'Oujda': "l'Oriental",
    'Berkane': "l'Oriental",
    'Figuig': "l'Oriental",
    
    # 85 Remaining
    'Kasba Tadla': 'Béni Mellal-Khénifra', 'Fqih Ben Salah': 'Béni Mellal-Khénifra', 'Souk Sebt': 'Béni Mellal-Khénifra',
    'Oulad Ayad': 'Béni Mellal-Khénifra', 'Dar Oulad Zidouh': 'Béni Mellal-Khénifra', 'Bradia': 'Béni Mellal-Khénifra',
    'El Hajeb': 'Fès-Meknès',
    'Mehdia': 'Rabat-Salé-Kénitra', 'Souq Larbaa': 'Rabat-Salé-Kénitra', 'Sidi Kacem': 'Rabat-Salé-Kénitra',
    'Sidi Slimane': 'Rabat-Salé-Kénitra', 'Sidi Yahya': 'Rabat-Salé-Kénitra', 'Bouknadel': 'Rabat-Salé-Kénitra',
    'Benslimane': 'Casablanca-Settat', 'Dar Bouazza': 'Casablanca-Settat', 'Sidi Rahal': 'Casablanca-Settat',
    'Bir Jdid': 'Casablanca-Settat', 'Sidi Bouzid': 'Casablanca-Settat', 'Khemis Zemamra': 'Casablanca-Settat',
    'Had Ouled Frej': 'Casablanca-Settat', 'Berrechid': 'Casablanca-Settat', 'El Gara': 'Casablanca-Settat',
    'Ben Ahmed': 'Casablanca-Settat',
    'Sebt Gzoula': 'Marrakech-Safi', 'Echemmaia': 'Marrakech-Safi', 'Sebkha Zima': 'Marrakech-Safi',
    'Oued Zem': 'Béni Mellal-Khénifra', 'Bejaad': 'Béni Mellal-Khénifra', 'Hattane': 'Béni Mellal-Khénifra',
    'Rommani': 'Rabat-Salé-Kénitra', 'Maaziz': 'Rabat-Salé-Kénitra', 'Tiddas': 'Rabat-Salé-Kénitra',
    'Oulmes': 'Rabat-Salé-Kénitra', 'Khemisset': 'Rabat-Salé-Kénitra', 'Mechra Bel Ksiri': 'Rabat-Salé-Kénitra',
    'Sidi Allal Tazi': 'Rabat-Salé-Kénitra',
    'Legzira': 'Souss-Massa', 'Sidi Bibi': 'Souss-Massa', 'Massa': 'Souss-Massa', 'Belfaa': 'Souss-Massa',
    'Biougra': 'Souss-Massa', 'Ait Baha': 'Souss-Massa', 'Igherm': 'Souss-Massa', 'Ida Ougnidif': 'Souss-Massa',
    'Oumesnat': 'Souss-Massa', 'Imsouane': 'Souss-Massa', 'Imi Ouaddar': 'Souss-Massa', 'Anza': 'Souss-Massa',
    'Aglou': 'Souss-Massa', 'Temsia': 'Souss-Massa', 'Ait Amira': 'Souss-Massa',
    'Akka': 'Drâa-Tafilalet', "M'Hamid": 'Drâa-Tafilalet', 'Tinfou': 'Drâa-Tafilalet', 'Tagounite': 'Drâa-Tafilalet',
    "M'Semrir": 'Drâa-Tafilalet', 'Tilmi': 'Drâa-Tafilalet', 'Khamlia': 'Drâa-Tafilalet', 'Taouz': 'Drâa-Tafilalet',
    'Ighri': 'Drâa-Tafilalet', 'Ghoust': 'Drâa-Tafilalet', 'Tizgui': 'Drâa-Tafilalet',
    'Amtoudi': 'Guelmim-Oued Noun', 'El Ouatia': 'Guelmim-Oued Noun', 'Icht': 'Guelmim-Oued Noun',
    'Ait Bouguemez': 'Béni Mellal-Khénifra', 'Tabant': 'Béni Mellal-Khénifra', 'Ait Blal': 'Béni Mellal-Khénifra',
    'Abachkou': 'Béni Mellal-Khénifra', 'Agouti': 'Béni Mellal-Khénifra',
    'Aroumd': 'Marrakech-Safi', 'Setti Fatma': 'Marrakech-Safi', 'Aït Ourir': 'Marrakech-Safi', 'Sidi Kaouki': 'Marrakech-Safi',
    'Maân': 'Fès-Meknès', 'El Menzel': 'Fès-Meknès', 'Ribate El Kheir': 'Fès-Meknès', 'Bir Tam Tam': 'Fès-Meknès',
    'Sidi Harazem': 'Fès-Meknès',
    'Talsint': "l'Oriental", 'Tendrara': "l'Oriental", 'Bouanane': "l'Oriental",
    'Foum el Oued': 'Laâyoune-Sakia El Hamra', 'Akhfenir': 'Laâyoune-Sakia El Hamra', 'Khenifiss': 'Laâyoune-Sakia El Hamra',
    
    # Misc user requests
    'Foum Zguid': 'Souss-Massa',
    'Tanger': 'Tanger-Tétouan-Al Hoceïma',
}

generic_mappings = {
    'Marrakesh-Safi': 'Marrakech-Safi',
    'Oriental': "l'Oriental",
    "Région de l'Oriental": "l'Oriental",
    "Rgion de l'Oriental": "l'Oriental",
    'Tanger-Tetouan-Al Hoceima': 'Tanger-Tétouan-Al Hoceïma',
    'Fs-Mekns': 'Fès-Meknès',
    'Rabat-Sal-Knitra': 'Rabat-Salé-Kénitra',
    'Bni Mellal-Khnifra': 'Béni Mellal-Khénifra',
    'Dra-Tafilalet': 'Drâa-Tafilalet',
    'Layoune-Sakia El Hamra': 'Laâyoune-Sakia El Hamra',
}

with engine.begin() as conn:
    for city, region in city_region_mapping.items():
        conn.execute(text("UPDATE destination SET continent = :r WHERE name = :c"), {"r": region, "c": city})
        
    for bad_reg, good_reg in generic_mappings.items():
        conn.execute(text("UPDATE destination SET continent = :g WHERE continent = :b"), {"g": good_reg, "b": bad_reg})

df = pd.read_sql("SELECT name, continent FROM destination WHERE continent IN ('Sud-Ouest', 'Centre', 'Sud-Est', 'Ouest')", engine)
print("Remaining generic mapping destinations:", len(df))
if len(df) > 0:
    print(df.to_string())

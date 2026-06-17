import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:Kxsd2882@localhost:5432/touristes_db')

query = """
SELECT name, continent 
FROM destination 
WHERE continent NOT IN (
    'Tanger-Tétouan-Al Hoceïma',  
    'Fès-Meknès', 
    'Rabat-Salé-Kénitra', 
    'Béni Mellal-Khénifra', 
    'Casablanca-Settat', 
    'Marrakech-Safi', 
    'Drâa-Tafilalet', 
    'Souss-Massa', 
    'Guelmim-Oued Noun', 
    'Laâyoune-Sakia El Hamra', 
    'Dakhla-Oued Ed-Dahab'
)
"""

df = pd.read_sql(query, engine)
print("Total incorrect:", len(df))

# Let's print the first 50 to see what we are dealing with
print(df.head(50).to_string())

# Also print all distinct wrong regions and their counts
print("\nCounts of wrong regions:")
counts = df['continent'].value_counts()
print(counts.head(20).to_string())

import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Kxsd2882@localhost:5432/touristes_db')
df = pd.read_sql("""
SELECT d.name, d.image_url
FROM destination d
WHERE d.name IN ('Chefchaouen', 'Marrakech', 'Merzouga', 'Essaouira', 'Cascades d''Ouzoud', 'Fes', 'Agadir', 'Ifrane')
""", engine)
print(df.to_string())

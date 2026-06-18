import pandas as pd
import numpy as np

df = pd.read_csv('tourisme_dataset.csv')
df.columns = [c.lower() for c in df.columns]

print('=== DATASET ANALYSIS ===')
print(f'Total rows: {len(df)}')
print(f'Unique destinations: {df["destination"].nunique()}')
print()
print('=== COLUMN NAMES IN CSV ===')
print(df.columns.tolist())
print()

FEATURE_COLS = ['age', 'budget', 'duree', 'interet', 'activite', 'climat', 'saison', 'region', 'type_voyage']
print('=== FEATURE COLUMN CHECK ===')
for c in FEATURE_COLS:
    if c in df.columns:
        vals = list(df[c].unique()[:8])
        print(f'  {c}: {df[c].nunique()} unique -> {vals}')
    else:
        print(f'  !! MISSING: {c} -- Available similar: {[x for x in df.columns if c[:4] in x]}')

print()
print('=== INTERET UNIQUE VALUES ===')
print(sorted(df['interet'].unique()))

print()
print('=== INTERET -> TYPE_DESTINATION ===')
cross = pd.crosstab(df['interet'], df['type_destination'])
print(cross)

print()
print('=== TOP 20 DESTINATIONS BY COUNT ===')
print(df['destination'].value_counts().head(20))

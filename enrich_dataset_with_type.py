"""
enrich_dataset_with_type.py
Adds 'Type_Destination' column to tourisme_dataset.csv by joining
with morocco_data.json, then retrains the model to predict destination TYPE
(6 classes) instead of exact city (252 classes).
This dramatically improves accuracy: 6 classes vs 252.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import pandas as pd

# Build destination -> type mapping from morocco_data.json
with open("morocco_data.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

dest_to_type = {city["name"]: city.get("type", "Ville") for city in cities}

# Load existing CSV
df = pd.read_csv("tourisme_dataset.csv")

print(f"CSV before: {len(df)} rows, columns: {list(df.columns)}")

# Add Type_Destination column
df["Type_Destination"] = df["Destination"].map(dest_to_type)

# Check how many rows got mapped
unmapped = df["Type_Destination"].isna().sum()
print(f"Unmapped destinations: {unmapped}")

# Fill unmapped with 'Ville' (safe fallback)
df["Type_Destination"].fillna("Ville", inplace=True)

# Show the type distribution
print("Type distribution:")
print(df["Type_Destination"].value_counts())

# Save enriched CSV
df.to_csv("tourisme_dataset.csv", index=False)
print(f"[OK] Saved enriched dataset with Type_Destination column")

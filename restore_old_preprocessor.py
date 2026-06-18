"""
restore_old_preprocessor.py
============================
Recrée l'ancien preprocessor.joblib compatible avec recommendation_model.joblib (ancien).
A exécuter UNIQUEMENT pour remettre le backend en état pendant le réentraînement.
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Import de l'ANCIEN FeatureCreator (celui qui existait avant notre refactoring)
import sys
sys.path.insert(0, '.')

# On recharge le dataset ORIGINAL (pas le clean) pour fitter le bon preprocessor
print("Loading original dataset...")
df = pd.read_csv('tourisme_dataset.csv')
df.drop_duplicates(inplace=True)
df.columns = [c.lower() for c in df.columns]
df.dropna(subset=['type_destination'], inplace=True)

FEATURE_COLS = ['age', 'budget', 'duree', 'interet', 'activite', 'climat', 'saison', 'region', 'type_voyage']
X = df[FEATURE_COLS]

# Vérifier les encodeurs existants
le_city = joblib.load('label_encoder.joblib')
print(f"Label encoder classes: {len(le_city.classes_)}")

# Reconstruire le preprocessor avec l'ANCIEN FeatureCreator
from transformers import FeatureCreator

categorical_features = [
    'interet', 'activite', 'climat', 'type_voyage', 'saison', 'region',
    'age_group', 'budget_level', 'region_interest', 'type_interest',
    'age_interest', 'season_climate_type', 'activity_climate_match',
    'profile_signature'
]
numerical_features = ['age', 'budget', 'duree', 'budget_per_day', 'age_budget_interaction', 'is_luxury']

preprocessor_step = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), categorical_features),
    ],
    remainder='drop'
)

full_pipeline = Pipeline(steps=[
    ('feature_creator', FeatureCreator()),
    ('preprocessor', preprocessor_step)
])

print("Fitting old preprocessor on original dataset...")
full_pipeline.fit(X)
joblib.dump(full_pipeline, 'preprocessor.joblib')
print("Done! Old preprocessor restored. Restart the backend now.")

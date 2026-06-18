"""
train_clean_model.py
====================
Re-entraîne le modèle de recommandation sur le dataset propre.
Features exactement alignées avec le frontend ForYou.jsx.
"""
import pandas as pd
import numpy as np
import joblib
import traceback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.base import BaseEstimator, TransformerMixin
from dotenv import load_dotenv

load_dotenv()

# ─── FEATURE CREATOR (simplified, no noisy derived features) ────────────────────
class CleanFeatureCreator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()

        X_['duree']  = pd.to_numeric(X_.get('duree',  0), errors='coerce').fillna(0)
        X_['budget'] = pd.to_numeric(X_.get('budget', 0), errors='coerce').fillna(0)
        X_['age']    = pd.to_numeric(X_.get('age',    0), errors='coerce').fillna(0)

        # Budget per day
        X_['budget_per_day'] = (X_['budget'] / (X_['duree'] + 1e-6)).clip(0, 1e6)

        # Age group
        def age_group(a):
            if a < 26:  return 'Jeune'
            if a < 46:  return 'Adulte'
            if a < 66:  return 'Senior'
            return 'Retraité'

        def budget_level(b):
            if b < 500:  return 'Petit'
            if b < 1200: return 'Moyen'
            if b < 3000: return 'Luxe'
            return 'Ultra-Luxe'

        X_['age_group']    = X_['age'].apply(age_group)
        X_['budget_level'] = X_['budget_per_day'].apply(budget_level)
        X_['is_luxury']    = X_['budget_level'].apply(lambda x: 1 if x in ['Luxe', 'Ultra-Luxe'] else 0)

        # Key interaction: interet + type + climat
        X_['interet_type']   = X_['interet'].astype(str) + '_' + X_['type_destination'].astype(str)
        X_['interet_climat'] = X_['interet'].astype(str) + '_' + X_['climat'].astype(str)
        X_['type_saison']    = X_['type_destination'].astype(str) + '_' + X_['saison'].astype(str)

        return X_


# ─── LOAD CLEAN DATASET ──────────────────────────────────────────────────────────
print("Loading clean dataset...")
df = pd.read_csv('tourisme_dataset_clean.csv')
df.drop_duplicates(inplace=True)

print(f"Rows: {len(df)} | Destinations: {df['destination'].nunique()}")
print(f"Interet values: {sorted(df['interet'].unique())}")

# ─── FEATURES & TARGETS ──────────────────────────────────────────────────────────
FEATURE_COLS = ['age', 'budget', 'duree', 'interet', 'activite', 'climat',
                'saison', 'region', 'type_voyage', 'type_destination']

X = df[FEATURE_COLS]
y_city = df['destination']
y_zone = df['zone']

# Encode targets
le_city = LabelEncoder()
y_city_enc = le_city.fit_transform(y_city)
joblib.dump(le_city, 'label_encoder.joblib')

le_zone = LabelEncoder()
y_zone_enc = le_zone.fit_transform(y_zone)
joblib.dump(le_zone, 'zone_encoder.joblib')

print(f"City classes: {len(le_city.classes_)} | Zone classes: {len(le_zone.classes_)}")

# ─── SPLIT ───────────────────────────────────────────────────────────────────────
indices = np.arange(len(X))
X_train, X_test, idx_train, idx_test = train_test_split(
    X, indices, test_size=0.2, random_state=42, stratify=y_city_enc
)
y_city_train, y_city_test = y_city_enc[idx_train], y_city_enc[idx_test]
y_zone_train, y_zone_test = y_zone_enc[idx_train], y_zone_enc[idx_test]

# ─── PREPROCESSING PIPELINE ──────────────────────────────────────────────────────
categorical_features = [
    'interet', 'activite', 'climat', 'type_voyage', 'saison', 'region',
    'type_destination', 'age_group', 'budget_level',
    'interet_type', 'interet_climat', 'type_saison'
]
numerical_features = ['age', 'budget', 'duree', 'budget_per_day', 'is_luxury']

preprocessor_step = ColumnTransformer(transformers=[
    ('num', StandardScaler(), numerical_features),
    ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), categorical_features),
], remainder='drop')

full_pipeline = Pipeline(steps=[
    ('feature_creator', CleanFeatureCreator()),
    ('preprocessor', preprocessor_step)
])

print("Fitting preprocessing pipeline...")
full_pipeline.fit(X_train)
joblib.dump(full_pipeline, 'preprocessor.joblib')
print("  Saved preprocessor.joblib")

X_train_proc = full_pipeline.transform(X_train).astype(np.float32)
X_test_proc  = full_pipeline.transform(X_test).astype(np.float32)

print(f"  Feature shape: {X_train_proc.shape}")

# ─── STAGE 1: ZONE MODEL ─────────────────────────────────────────────────────────
print(f"\n--- Stage 1: Zone Model ({len(le_zone.classes_)} classes) ---")
zone_model = RandomForestClassifier(
    n_estimators=80, max_depth=18, min_samples_split=6,
    min_samples_leaf=3, random_state=42, n_jobs=2
)
zone_model.fit(X_train_proc, y_zone_train)
joblib.dump(zone_model, 'zone_model.joblib', compress=3)

zone_preds   = zone_model.predict(X_test_proc)
zone_acc     = accuracy_score(y_zone_test, zone_preds)
print(f"  Zone Test Accuracy: {zone_acc:.4f}")

# ─── STAGE 2: CITY MODEL ─────────────────────────────────────────────────────────
print(f"\n--- Stage 2: City Model ({len(le_city.classes_)} classes) ---")
city_model = RandomForestClassifier(
    n_estimators=120,   # Reduced from 200 to avoid MemoryError
    max_depth=28,       # Bounded to cap memory
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=2,           # Limit parallel workers to save RAM
    verbose=1
)
city_model.fit(X_train_proc, y_city_train)
joblib.dump(city_model, 'recommendation_model.joblib', compress=3)
print("  Saved recommendation_model.joblib")

# ─── EVALUATION ──────────────────────────────────────────────────────────────────
probas    = city_model.predict_proba(X_test_proc)
city_preds = np.argmax(probas, axis=1)
city_acc  = accuracy_score(y_city_test, city_preds)

def top_k_accuracy(y_true, probas, k=5):
    top_k = np.argpartition(probas, -k, axis=1)[:, -k:]
    return np.any(top_k == y_true[:, None], axis=1).mean()

city_top5 = top_k_accuracy(y_city_test, probas, k=5)

print(f"\n=== FINAL RESULTS ===")
print(f"Zone Test Accuracy: {zone_acc:.4f}")
print(f"City Top-1 Accuracy: {city_acc:.4f}")
print(f"City Top-5 Accuracy: {city_top5:.4f}")

with open('model_performance.txt', 'w', encoding='utf-8') as f:
    f.write(f"Clean Dataset Model Evaluation\n")
    f.write(f"Zone Test Accuracy: {zone_acc:.4f}\n")
    f.write(f"City Test Accuracy (Top-1): {city_acc:.4f}\n")
    f.write(f"City Test Accuracy (Top-5): {city_top5:.4f}\n")

print("\nAll models saved. Restart the backend to load the new models.")

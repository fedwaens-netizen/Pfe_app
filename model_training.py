import pandas as pd
import numpy as np
import joblib
import traceback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from dotenv import load_dotenv
from transformers import FeatureCreator

load_dotenv()

# --- Load data ---
print("Loading dataset...")
df = pd.read_csv('tourisme_dataset.csv')
df.drop_duplicates(inplace=True)

# Lowercase all columns for consistency
df.columns = [c.lower() for c in df.columns]

df.dropna(subset=['type_destination'], inplace=True)

# --- Features & Target ---
FEATURE_COLS = ['age', 'budget', 'duree', 'interet', 'activite', 'climat', 'saison', 'region', 'type_voyage']
X = df[FEATURE_COLS]
y_city = df['destination']
y_zone = df['zone']

print(f"Dataset summary: {len(df)} rows | {y_city.nunique()} destination classes")

# Encode Targets
le_city = LabelEncoder()
y_city_enc = le_city.fit_transform(y_city)
joblib.dump(le_city, 'label_encoder.joblib')

le_zone = LabelEncoder()
y_zone_enc = le_zone.fit_transform(y_zone)
joblib.dump(le_zone, 'zone_encoder.joblib')

# Combine targets for mapping (but we only train on city)
city_zone_mapping = df.drop_duplicates('destination').set_index('destination')['zone'].to_dict()
joblib.dump(city_zone_mapping, 'city_to_zone_map.joblib')

# Split indices to keep arrays aligned
indices = np.arange(len(X))
X_train, X_test, indices_train, indices_test = train_test_split(
    X, indices, test_size=0.2, random_state=42, stratify=y_city_enc
)

y_city_train, y_city_test = y_city_enc[indices_train], y_city_enc[indices_test]
y_zone_train, y_zone_test = y_zone_enc[indices_train], y_zone_enc[indices_test]

# Categorical features for Ordinal Encoding (including those created by FeatureCreator)
categorical_features = [
    'interet', 'activite', 'climat', 'type_voyage', 'saison', 'region', 
    'age_group', 'budget_level', 'region_interest', 'type_interest', 
    'age_interest', 'season_climate_type', 'activity_climate_match',
    'profile_signature'
]
numerical_features = ['age', 'budget', 'duree', 'budget_per_day', 'age_budget_interaction', 'is_luxury']

# Preprocessing
preprocessor_step = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), categorical_features),
    ],
    remainder='drop'
)

full_pipeline = Pipeline(steps=[
    ('feature_creator', FeatureCreator()),
    ('preprocessor', preprocessor_step),
])

print("Fitting preprocessing pipeline...")
full_pipeline.fit(X_train)
joblib.dump(full_pipeline, 'preprocessor.joblib')

X_train_proc = full_pipeline.transform(X_train).astype(np.float32)
X_test_proc  = full_pipeline.transform(X_test).astype(np.float32)

# --- Train Zone Model (Stage 1) ---
try:
    print(f"\n--- Stage 1: Training Zone Predictor on {X_train_proc.shape[0]} samples ---")
    zone_rf_params = {
        'n_estimators': 50,           
        'max_depth': 15,             
        'min_samples_split': 10,       
        'min_samples_leaf': 5,
        'random_state': 42,
        'n_jobs': 4,  # Changed from -1 to 4 to prevent Windows deadlock
        'verbose': 0                  
    }

    zone_model = RandomForestClassifier(**zone_rf_params)
    print(f"Fitting Zone Model on {len(le_zone.classes_)} classes...")
    zone_model.fit(X_train_proc, y_zone_train)
    joblib.dump(zone_model, 'zone_model.joblib', compress=3)

    print("Evaluating Zone Model...")
    zone_preds = zone_model.predict(X_test_proc)
    zone_acc = accuracy_score(y_zone_test, zone_preds)
    
    zone_train_idx = np.random.choice(len(X_train_proc), size=min(len(X_train_proc), 10000), replace=False)
    zone_train_acc = accuracy_score(y_zone_train[zone_train_idx], zone_model.predict(X_train_proc[zone_train_idx]))
    
    print(f"Zone Test Accuracy: {zone_acc:.4f}")
    print(f"Zone Train Accuracy: {zone_train_acc:.4f}\n")

    # --- Train City Model (Stage 2) ---
    print(f"--- Stage 2: Training City Predictor on {X_train_proc.shape[0]} samples ---")
    
    city_rf_params = {
        'n_estimators': 50,           
        'max_depth': 20,             
        'min_samples_split': 15,       
        'min_samples_leaf': 10,
        'random_state': 42,
        'n_jobs': 4,  # Changed from -1 to 4 to prevent Windows deadlock
        'verbose': 0                  
    }

    city_model = RandomForestClassifier(**city_rf_params)
    print(f"Fitting City Model on {len(le_city.classes_)} classes...")
    city_model.fit(X_train_proc, y_city_train)
    joblib.dump(city_model, 'recommendation_model.joblib', compress=3)

    # --- Evaluation ---
    print("Evaluating City Model...")
    probas_city = city_model.predict_proba(X_test_proc)

    def top_k_accuracy(y_true, probas, k=5):
        top_k_idx = np.argpartition(probas, -k, axis=1)[:, -k:]
        return np.any(top_k_idx == y_true[:, None], axis=1).mean()

    city_test_acc = accuracy_score(y_city_test, np.argmax(probas_city, axis=1))
    city_test_top5 = top_k_accuracy(y_city_test, probas_city, k=5)

    # Training Gap Check
    city_train_acc = accuracy_score(y_city_train[zone_train_idx], city_model.predict(X_train_proc[zone_train_idx]))

    print(f"\nFinal Results (City):")
    print(f"Test Accuracy: {city_test_acc:.4f}")
    print(f"Top-5 Accuracy: {city_test_top5:.4f}")
    print(f"Gap: {city_train_acc - city_test_acc:.4f}")

    # Save Performance
    with open('model_performance.txt', 'w', encoding='utf-8') as f:
        f.write(f"Hierarchical Models Evaluation\n")
        f.write(f"Zone Test Accuracy: {zone_acc:.4f}\n")
        f.write(f"City Test Accuracy (Top-1): {city_test_acc:.4f}\n")
        f.write(f"City Test Accuracy (Top-5): {city_test_top5:.4f}\n")

except Exception as e:
    print("Error during training or evaluation:")
    print(traceback.format_exc())
    exit(1)

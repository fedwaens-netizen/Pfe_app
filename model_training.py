import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import numpy as np
import os
from dotenv import load_dotenv
from transformers import FeatureCreator

load_dotenv()

# --- Load enriched training data from CSV ---
# CSV columns: Age, Budget, Interet, Duree, Climat, Type_Voyage, Saison,
#              Nationalite, Activite, Destination, Type_Destination
df = pd.read_csv('tourisme_dataset.csv')
df.drop_duplicates(inplace=True)

# Rename to lowercase to match FeatureCreator expectations
df.rename(columns={'Age': 'age', 'Budget': 'budget'}, inplace=True)

# Drop rows where Type_Destination is missing (shouldn't happen after enrichment)
df.dropna(subset=['Type_Destination'], inplace=True)

print(f"Training on {len(df)} rows  |  Classes: {sorted(df['Type_Destination'].unique())}")

# --- Features: predict destination TYPE (6 classes) not exact city (252 classes) ---
FEATURE_COLS = ['age', 'budget', 'Duree', 'Interet', 'Climat', 'Type_Voyage', 'Saison', 'Nationalite', 'Activite']
X = df[FEATURE_COLS]
y = df['Type_Destination']   # TARGET: 6-class type prediction

# Encode target
le = LabelEncoder()
y_encoded = le.fit_transform(y)
joblib.dump(le, 'label_encoder.joblib')

# Stratified split to keep class balance in both train/test
X_train, X_test, y_train_enc, y_test_enc = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Features handled after FeatureCreator adds Budget_per_day
categorical_features = ['Interet', 'Climat', 'Type_Voyage', 'Saison', 'Nationalite', 'Activite']
numerical_features   = ['age', 'budget', 'Duree', 'Budget_per_day']

# Preprocessing pipeline
preprocessor_step = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(),              numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
    ],
    remainder='drop'
)

full_pipeline = Pipeline(steps=[
    ('feature_creator', FeatureCreator()),
    ('preprocessor', preprocessor_step),
])

full_pipeline.fit(X_train)
joblib.dump(full_pipeline, 'preprocessor.joblib')

X_train_proc = full_pipeline.transform(X_train)
X_test_proc  = full_pipeline.transform(X_test)

# Train model — 150 trees is fast for 6 classes but robust
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=20,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train_proc, y_train_enc)
joblib.dump(model, 'recommendation_model.joblib')

# Evaluate
y_pred_enc = model.predict(X_test_proc)
accuracy   = accuracy_score(y_test_enc, y_pred_enc)
report     = classification_report(
    y_test_enc, y_pred_enc,
    labels=range(len(le.classes_)),
    target_names=le.classes_,
    zero_division=0
)

with open('model_performance.txt', 'w') as f:
    f.write(f"Target: Destination TYPE ({len(le.classes_)} classes)\n")
    f.write(f"Accuracy: {accuracy:.4f}\n\n")
    f.write("Classification Report:\n")
    f.write(report)

print(f"Accuracy: {accuracy:.4f}  (predicting TYPE among {len(le.classes_)} classes)")
print(f"Classes: {list(le.classes_)}")

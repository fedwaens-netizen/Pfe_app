import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureCreator(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        X_ = X.copy()

        X_['duree']  = pd.to_numeric(X_.get('duree',  0), errors='coerce').fillna(0)

        X_['budget'] = pd.to_numeric(X_.get('budget', 0), errors='coerce').fillna(0)

        X_['age']    = pd.to_numeric(X_.get('age',    0), errors='coerce').fillna(0)

        X_['budget_per_day'] = (X_['budget'] / (X_['duree'] + 1e-6)).clip(0, 1e6)

        def age_group(a):

            if a < 26: return 'Jeune'

            if a < 46: return 'Adulte'

            if a < 66: return 'Senior'

            return 'Retraite'

        def budget_level(b):

            if b < 500:  return 'Petit'

            if b < 1200: return 'Moyen'

            if b < 3000: return 'Luxe'

            return 'Ultra-Luxe'

        X_['age_group']      = X_['age'].apply(age_group)

        X_['budget_level']   = X_['budget_per_day'].apply(budget_level)

        X_['is_luxury']      = X_['budget_level'].apply(lambda x: 1 if x in ['Luxe', 'Ultra-Luxe'] else 0)

        X_['interet_type']   = X_['interet'].astype(str) + '_' + X_['type_destination'].astype(str)

        X_['interet_climat'] = X_['interet'].astype(str) + '_' + X_['climat'].astype(str)

        X_['type_saison']    = X_['type_destination'].astype(str) + '_' + X_['saison'].astype(str)
        
        return X_


data = pd.read_csv("dataset.csv")

data.drop_duplicates(inplace=True)

print(f"nb_lignes: {len(data)} | nb_destination: {data['destination'].nunique()}")

Features = ['age', 'budget', 'duree', 'interet', 'activite', 'climat',

            'saison', 'region', 'type_voyage', 'type_destination']

X = data[Features]

y_destination = data['destination']

y_zone = data['zone']


destination_enc = LabelEncoder()

y_destination_enc = destination_enc.fit_transform(y_destination)

print(f"Destination classes: {len(destination_enc.classes_)}")

zone_enc = LabelEncoder()

y_zone_enc = zone_enc.fit_transform(y_zone)

print(f"Zone classes: {len(zone_enc.classes_)}")

indices = np.arange(len(X))

X_train, X_test, idx_train, idx_test = train_test_split(

    X, indices, test_size=0.2, random_state=42, stratify=y_destination_enc)

y_destination_train = y_destination_enc[idx_train]

y_destination_test  = y_destination_enc[idx_test]

y_zone_train = y_zone_enc[idx_train]

y_zone_test  = y_zone_enc[idx_test]


features_categorielles = [

    'interet', 'activite', 'climat', 'type_voyage', 'saison', 'region',

    'type_destination', 'age_group', 'budget_level',

    'interet_type', 'interet_climat', 'type_saison']

features_numeriques = ['age', 'budget', 'duree', 'budget_per_day', 'is_luxury']

preprocessor_step = ColumnTransformer(

    transformers=[

        ('num', StandardScaler(), features_numeriques),

        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), features_categorielles),]
    
         ,remainder='drop')

pipeline = Pipeline(steps=[

    ('feature_creator', FeatureCreator()),

    ('preprocessor', preprocessor_step)])


pipeline.fit(X_train)

X_train_proc = pipeline.transform(X_train).astype(np.float32)

X_test_proc  = pipeline.transform(X_test).astype(np.float32)

print(f"dimensions de X_train : {X_train_proc.shape}")

print(f"dimensions de X_test: {X_test_proc.shape}")

modele1 = RandomForestClassifier(

    n_estimators=80, max_depth=18, min_samples_split=6,

    min_samples_leaf=3, random_state=42, n_jobs=2)

modele1.fit(X_train_proc, y_zone_train)

acc_zone = accuracy_score(y_zone_test, modele1.predict(X_test_proc))

print(f"Accuracy des Zones: {acc_zone:.4f}")

modele2 = RandomForestClassifier(

    n_estimators=40, max_depth=12, min_samples_split=10,

    min_samples_leaf=5, random_state=42, n_jobs=2, verbose=1)

modele2.fit(X_train_proc, y_destination_train)

proba = modele2.predict_proba(X_test_proc)

acc_destination = accuracy_score(y_destination_test, np.argmax(proba, axis=1))

def top_k_destination(y_true, probas, k=5):

    top = np.argpartition(probas, -k, axis=1)[:, -k:]

    return np.any(top == y_true[:, None], axis=1).mean()

top5_destination = top_k_destination(y_destination_test, proba, k=5)

print(f"Accuracy des Zones        : {acc_zone:.4f}")

print(f"Accuracy des Destinations : {acc_destination:.4f}")

print(f"Top-5 des Destinations    : {top5_destination:.4f}")


print("\nSaving models...")

joblib.dump(pipeline,        'preprocessor.joblib')

joblib.dump(modele2,         'recommendation_model.joblib', compress=3)

joblib.dump(modele1,         'zone_model.joblib',           compress=3)

joblib.dump(destination_enc, 'label_encoder.joblib')

joblib.dump(zone_enc,        'zone_encoder.joblib')

with open('model_performance.txt', 'w', encoding='utf-8') as f:

    f.write(f"Clean Dataset Model\n")

    f.write(f"Zone Accuracy  : {acc_zone:.4f}\n")

    f.write(f"City Top-1     : {acc_destination:.4f}\n")

    f.write(f"City Top-5     : {top5_destination:.4f}\n")

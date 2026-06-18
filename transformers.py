import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureCreator(BaseEstimator, TransformerMixin):
    """
    Feature engineering step that matches train_clean_model.py exactly.
    Inputs: age, budget, duree, interet, activite, climat, saison,
            region, type_voyage, type_destination
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()

        # ── Numeric safety ────────────────────────────────────────────────────────
        X_['duree']  = pd.to_numeric(X_.get('duree',  0), errors='coerce').fillna(0)
        X_['budget'] = pd.to_numeric(X_.get('budget', 0), errors='coerce').fillna(0)
        X_['age']    = pd.to_numeric(X_.get('age',    0), errors='coerce').fillna(0)

        # ── Budget per day ────────────────────────────────────────────────────────
        X_['budget_per_day'] = (X_['budget'] / (X_['duree'] + 1e-6)).clip(0, 1e6)

        # ── Age group ─────────────────────────────────────────────────────────────
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

        # ── Key semantic interactions ─────────────────────────────────────────────
        interet  = X_['interet'].astype(str)
        dest_t   = X_['type_destination'].astype(str)
        climat   = X_['climat'].astype(str)
        saison   = X_['saison'].astype(str)

        X_['interet_type']   = interet + '_' + dest_t
        X_['interet_climat'] = interet + '_' + climat
        X_['type_saison']    = dest_t  + '_' + saison

        return X_

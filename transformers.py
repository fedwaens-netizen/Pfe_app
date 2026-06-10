import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Custom Transformer for creating new features
class FeatureCreator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        
        # Ensure numeric
        X_['duree'] = pd.to_numeric(X_.get('duree', 0), errors='coerce').fillna(0)
        X_['budget'] = pd.to_numeric(X_.get('budget', 0), errors='coerce').fillna(0)
        X_['age'] = pd.to_numeric(X_.get('age', 0), errors='coerce').fillna(0)
        
        # 1. Budget per day
        X_['budget_per_day'] = X_['budget'] / (X_['duree'] + 1e-6)
        import numpy as np
        X_['budget_per_day'] = X_['budget_per_day'].replace([np.inf, -np.inf], 0)
        
        # 2. Age-Budget Interaction
        X_['age_budget_interaction'] = X_['age'] * X_['budget_per_day']
        
        # 3. Categorical Derived Features
        def get_age_group(age):
            if age < 26: return 'Jeune'
            elif age < 46: return 'Adulte'
            elif age < 66: return 'Senior'
            else: return 'Retraité'
            
        def get_budget_level(daily_budget):
            if daily_budget < 600: return 'Petit'
            elif daily_budget < 1300: return 'Moyen'
            elif daily_budget < 2800: return 'Luxe'
            else: return 'Ultra-Luxe'

        X_['age_group'] = X_['age'].apply(get_age_group)
        X_['budget_level'] = X_['budget_per_day'].apply(get_budget_level)

        # 4. Categorical Interactions (Case-insensitive where possible)
        def clean_str(v): return str(v).strip().capitalize()
        
        X_['region_interest'] = X_.get('region', 'Toutes').apply(clean_str) + "_" + X_.get('interet', 'Inconnu').apply(clean_str)
        X_['type_interest'] = X_.get('type_voyage', 'Solo').apply(clean_str) + "_" + X_.get('interet', 'Inconnu').apply(clean_str)
        X_['age_interest'] = X_['age_group'].apply(clean_str) + "_" + X_.get('interet', 'Inconnu').apply(clean_str)
        
        # 5. Season-Climate Match (More robust matching)
        def get_season_climate(row):
            s = str(row.get('saison', '')).lower()
            c = str(row.get('climat', '')).lower()
            if ('ét' in s or 'summer' in s) and ('chaud' in c or 'désert' in c):
                return "Extreme_Hot"
            if ('hiv' in s or 'winter' in s) and ('froid' in c or 'cold' in c):
                return "Extreme_Cold"
            return "Moderate"
            
        X_['season_climate_type'] = X_.apply(get_season_climate, axis=1)

        # 6. Activity-Climate Match
        def get_act_cli_match(row):
            act = str(row.get('activite', '')).lower()
            cli = str(row.get('climat', '')).lower()
            if any(x in act for x in ['surf', 'plage', 'plong']) and ('humid' in cli or 'temp' in cli):
                return "Coastal_Match"
            if any(x in act for x in ['ski', 'rand']) and ('froid' in cli or 'temp' in cli):
                return "Mountain_Match"
            return "Standard"
            
        X_['activity_climate_match'] = X_.apply(get_act_cli_match, axis=1)
        
        # 7. Profile Signature (Combining key lifestyle traits) - use clean_str for stability
        X_['profile_signature'] = (
            X_['age_group'].apply(clean_str) + "_" + 
            X_['budget_level'].apply(clean_str) + "_" + 
            X_.get('saison', 'Inconnue').apply(clean_str)
        )
        
        # 8. Luxury Flag
        X_['is_luxury'] = X_['budget_level'].apply(lambda x: 1 if x in ['Luxe', 'Ultra-Luxe'] else 0)
        
        return X_


import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Custom Transformer for creating new features
class FeatureCreator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_['Duree'] = pd.to_numeric(X_['Duree'], errors='coerce').fillna(0)
        X_['budget'] = pd.to_numeric(X_['budget'], errors='coerce').fillna(0)
        X_['Budget_per_day'] = X_['budget'] / (X_['Duree'] + 1e-6)
        # Removed Interet_Continent interaction (continent feature removed)
        return X_

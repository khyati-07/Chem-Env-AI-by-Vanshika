"""
Pollution prediction model.
Uses Random Forest and XGBoost to predict AQI or pollutant concentration.
"""
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor


class PollutionPredictor:
    """
    Predicts a continuous pollution target (e.g., AQI, PM2.5 concentration).
    Supports Random Forest and XGBoost backends.
    """

    SUPPORTED_MODELS = {"random_forest", "xgboost"}

    def __init__(self, model_type: str = "xgboost", random_state: int = 42):
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"model_type must be one of {self.SUPPORTED_MODELS}")
        self.model_type = model_type
        self.random_state = random_state
        self.model = self._build_model()
        self.is_trained = False

    def _build_model(self):
        if self.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=self.random_state,
                n_jobs=-1,
            )
        return XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.random_state,
            verbosity=0,
        )

    def train(self, X, y, test_size: float = 0.2):
        """Fit model and return evaluation metrics on hold-out set."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        metrics = {
            "MAE":  round(mean_absolute_error(y_test, y_pred), 4),
            "R2":   round(r2_score(y_test, y_pred), 4),
            "test_size": len(y_test),
        }
        return metrics

    def cross_validate(self, X, y, cv: int = 5):
        """Return mean and std of cross-validated R2 scores."""
        scores = cross_val_score(self.model, X, y, cv=cv, scoring="r2", n_jobs=-1)
        return {"cv_r2_mean": round(scores.mean(), 4), "cv_r2_std": round(scores.std(), 4)}

    def predict(self, X) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling predict().")
        return self.model.predict(X)

    def feature_importances(self, feature_names: list) -> dict:
        """Return feature importances sorted descending."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained first.")
        importances = self.model.feature_importances_
        return dict(sorted(zip(feature_names, importances), key=lambda x: -x[1]))

    def save(self, path: str):
        joblib.dump(self.model, path)

    def load(self, path: str):
        self.model = joblib.load(path)
        self.is_trained = True

import pytest
import numpy as np
from src.data.loader import load_sample_air_quality
from src.data.preprocessor import (
    clean_air_quality, engineer_air_features,
    encode_categoricals, split_features_target
)
from src.models.pollution_predictor import PollutionPredictor
from src.models.remediation_advisor import RemediationAdvisor


FEATURE_COLS = ["PM2_5", "PM10", "NO2", "O3", "CO",
                "temperature_C", "humidity_pct", "wind_speed_ms"]


def _get_prepared_data():
    df = load_sample_air_quality()
    df = clean_air_quality(df)
    df = engineer_air_features(df)
    df = encode_categoricals(df, columns=["location", "season", "pollution_level"])
    X, y = split_features_target(df, target="AQI", drop_cols=["date"])
    X = X[[c for c in FEATURE_COLS if c in X.columns]]
    return X, y


def test_predictor_trains_and_evaluates():
    X, y = _get_prepared_data()
    predictor = PollutionPredictor(model_type="xgboost")
    metrics = predictor.train(X, y)
    assert "MAE" in metrics
    assert "R2" in metrics
    assert metrics["R2"] > 0.5, "R2 should be reasonably high on synthetic data"


def test_predictor_predict_shape():
    X, y = _get_prepared_data()
    predictor = PollutionPredictor(model_type="random_forest")
    predictor.train(X, y)
    preds = predictor.predict(X)
    assert len(preds) == len(X)
    assert all(isinstance(v, (float, np.floating)) for v in preds)


def test_predictor_untrained_raises():
    predictor = PollutionPredictor()
    with pytest.raises(RuntimeError):
        predictor.predict([[1, 2, 3]])


def test_feature_importances_keys():
    X, y = _get_prepared_data()
    predictor = PollutionPredictor(model_type="xgboost")
    predictor.train(X, y)
    importances = predictor.feature_importances(list(X.columns))
    assert set(importances.keys()) == set(X.columns)


def test_rule_based_remediation_high_pm():
    advisor = RemediationAdvisor()
    result = advisor.rule_based_recommend({"PM2_5": 120, "NO2": 50})
    assert "air_high_PM" in result
    assert len(result["air_high_PM"]) > 0


def test_rule_based_remediation_clean():
    advisor = RemediationAdvisor()
    result = advisor.rule_based_recommend({"PM2_5": 10, "NO2": 5})
    assert "status" in result


def test_rule_based_remediation_water():
    advisor = RemediationAdvisor()
    result = advisor.rule_based_recommend({"lead_ugl": 15, "arsenic_ugl": 8})
    assert "water_high_lead" in result
    assert "water_high_arsenic" in result

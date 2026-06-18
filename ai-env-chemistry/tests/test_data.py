import pytest
import pandas as pd
from src.data.loader import load_sample_air_quality, load_sample_water_quality
from src.data.preprocessor import (
    clean_air_quality, engineer_air_features,
    encode_categoricals, split_features_target
)


def test_air_quality_loader_shape():
    df = load_sample_air_quality()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 500
    assert "AQI" in df.columns
    assert "pollution_level" in df.columns


def test_water_quality_loader_shape():
    df = load_sample_water_quality()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 400
    assert "contaminated" in df.columns


def test_clean_air_quality_no_missing():
    df = load_sample_air_quality()
    cleaned = clean_air_quality(df)
    numeric_cols = cleaned.select_dtypes(include="number").columns
    assert cleaned[numeric_cols].isnull().sum().sum() == 0


def test_engineer_air_features_adds_columns():
    df = load_sample_air_quality()
    df = engineer_air_features(df)
    assert "month" in df.columns
    assert "day_of_week" in df.columns
    assert "season" in df.columns
    assert "heat_stagnation" in df.columns


def test_split_features_target():
    df = load_sample_air_quality()
    X, y = split_features_target(df, target="AQI", drop_cols=["date", "pollution_level"])
    assert "AQI" not in X.columns
    assert len(X) == len(y)

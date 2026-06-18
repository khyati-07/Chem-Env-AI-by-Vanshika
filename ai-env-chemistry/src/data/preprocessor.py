"""
Preprocessing pipelines for environmental pollution data.
Handles missing values, feature engineering, and scaling.
"""
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer


def clean_air_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicates, handle outliers, and fill missing values."""
    df = df.drop_duplicates()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Cap extreme outliers at 99th percentile
    for col in numeric_cols:
        upper = df[col].quantile(0.99)
        df[col] = df[col].clip(upper=upper)

    # Fill missing numeric values with column median
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    return df.reset_index(drop=True)


def engineer_air_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add temporal and interaction features."""
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df["day_of_week"] = df["date"].dt.dayofweek
        df["season"] = df["month"].apply(_month_to_season)

    # Interaction: high temp + low wind -> pollution accumulation risk
    if "temperature_C" in df.columns and "wind_speed_ms" in df.columns:
        df["heat_stagnation"] = df["temperature_C"] / (df["wind_speed_ms"] + 0.1)

    return df


def _month_to_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    return "Autumn"


def build_numeric_pipeline() -> Pipeline:
    """Return a sklearn pipeline for imputing and scaling numeric features."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])


def encode_categoricals(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Label-encode categorical columns in-place."""
    le = LabelEncoder()
    for col in columns:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))
    return df


def split_features_target(df: pd.DataFrame, target: str, drop_cols: list = None):
    """Return X, y after dropping target and any specified columns."""
    drop = [target] + (drop_cols or [])
    drop = [c for c in drop if c in df.columns]
    X = df.drop(columns=drop)
    y = df[target]
    return X, y

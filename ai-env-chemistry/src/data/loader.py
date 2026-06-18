"""
Data loader for environmental pollution datasets.
Supports CSV, JSON, and OpenAQ API formats.
"""
import os
import pandas as pd
import numpy as np


def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV pollution dataset from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")
    df = pd.read_csv(filepath, parse_dates=True)
    return df


def load_sample_air_quality() -> pd.DataFrame:
    """
    Generate a synthetic air quality dataset for demonstration.
    Columns: date, location, PM2.5, PM10, NO2, O3, CO, AQI, label
    """
    np.random.seed(42)
    n = 500
    dates = pd.date_range(start="2022-01-01", periods=n, freq="D")
    locations = np.random.choice(["SiteA", "SiteB", "SiteC", "SiteD"], size=n)

    df = pd.DataFrame({
        "date": dates,
        "location": locations,
        "PM2_5": np.random.lognormal(mean=2.5, sigma=0.6, size=n),   # µg/m³
        "PM10":  np.random.lognormal(mean=3.2, sigma=0.5, size=n),
        "NO2":   np.random.lognormal(mean=3.0, sigma=0.7, size=n),
        "O3":    np.random.lognormal(mean=3.5, sigma=0.4, size=n),
        "CO":    np.random.lognormal(mean=0.5, sigma=0.3, size=n),
        "temperature_C": np.random.normal(loc=20, scale=8, size=n),
        "humidity_pct":  np.random.uniform(30, 90, size=n),
        "wind_speed_ms": np.random.exponential(scale=3, size=n),
    })

    # Simulate AQI from PM2.5 (simplified)
    df["AQI"] = df["PM2_5"] * 4.5 + np.random.normal(0, 10, n)
    df["AQI"] = df["AQI"].clip(lower=0).round(1)

    # Label: Good <50, Moderate 50-100, Unhealthy >100
    df["pollution_level"] = pd.cut(
        df["AQI"],
        bins=[0, 50, 100, float("inf")],
        labels=["Good", "Moderate", "Unhealthy"]
    )
    return df


def load_sample_water_quality() -> pd.DataFrame:
    """
    Generate a synthetic water quality dataset.
    Columns: date, site, pH, dissolved_oxygen, nitrates, heavy metals, contaminated
    """
    np.random.seed(7)
    n = 400
    dates = pd.date_range(start="2022-01-01", periods=n, freq="D")
    sites = np.random.choice(["River_A", "Lake_B", "Groundwater_C"], size=n)

    df = pd.DataFrame({
        "date": dates,
        "site": sites,
        "pH":               np.random.normal(7.2, 0.8, n).clip(4, 10),
        "dissolved_oxygen": np.random.normal(8.5, 1.5, n).clip(0, 14),
        "nitrates_mgl":     np.abs(np.random.normal(5, 4, n)),
        "phosphates_mgl":   np.abs(np.random.normal(0.3, 0.2, n)),
        "lead_ugl":         np.abs(np.random.exponential(2, n)),
        "arsenic_ugl":      np.abs(np.random.exponential(1, n)),
        "turbidity_ntu":    np.abs(np.random.normal(3, 2, n)),
    })

    # Contamination flag: lead > 10 µg/L or arsenic > 5 µg/L
    df["contaminated"] = (
        (df["lead_ugl"] > 10) | (df["arsenic_ugl"] > 5)
    ).astype(int)
    return df

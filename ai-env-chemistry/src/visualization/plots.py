"""
Visualization utilities for environmental pollution analysis.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


sns.set_theme(style="whitegrid", palette="muted")


def plot_aqi_trend(df: pd.DataFrame, date_col: str = "date", aqi_col: str = "AQI",
                   location_col: str = "location", title: str = "AQI Over Time"):
    """Line chart of AQI over time, coloured by location."""
    fig, ax = plt.subplots(figsize=(12, 5))
    for loc, grp in df.groupby(location_col):
        grp_sorted = grp.sort_values(date_col)
        ax.plot(grp_sorted[date_col], grp_sorted[aqi_col], label=loc, alpha=0.8)
    ax.axhline(50, color="green", linestyle="--", linewidth=0.8, label="Good threshold (50)")
    ax.axhline(100, color="orange", linestyle="--", linewidth=0.8, label="Moderate threshold (100)")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("AQI")
    ax.legend()
    plt.tight_layout()
    return fig


def plot_pollution_distribution(df: pd.DataFrame, columns: list,
                                 title: str = "Pollutant Distributions"):
    """Box plots for multiple pollutant columns."""
    fig, axes = plt.subplots(1, len(columns), figsize=(4 * len(columns), 5))
    if len(columns) == 1:
        axes = [axes]
    for ax, col in zip(axes, columns):
        if col in df.columns:
            ax.boxplot(df[col].dropna(), vert=True, patch_artist=True,
                       boxprops=dict(facecolor="steelblue", alpha=0.6))
            ax.set_title(col)
            ax.set_ylabel("Concentration")
    fig.suptitle(title)
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, title: str = "Feature Correlation Heatmap"):
    """Seaborn heatmap of numeric feature correlations."""
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_feature_importance(importances: dict, top_n: int = 15,
                             title: str = "Feature Importances"):
    """Horizontal bar chart of top-N feature importances."""
    items = list(importances.items())[:top_n]
    features, values = zip(*items) if items else ([], [])
    fig, ax = plt.subplots(figsize=(8, 6))
    y_pos = range(len(features))
    ax.barh(y_pos, values, color="steelblue", alpha=0.8)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(list(features))
    ax.invert_yaxis()
    ax.set_xlabel("Importance")
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_actual_vs_predicted(y_true, y_pred, label: str = "AQI",
                              title: str = "Actual vs Predicted"):
    """Scatter plot comparing actual and predicted values."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(y_true, y_pred, alpha=0.5, s=20, color="steelblue")
    lim = [min(min(y_true), min(y_pred)), max(max(y_true), max(y_pred))]
    ax.plot(lim, lim, "r--", linewidth=1.2, label="Perfect prediction")
    ax.set_xlabel(f"Actual {label}")
    ax.set_ylabel(f"Predicted {label}")
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    return fig


def plot_contamination_map(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon",
                            value_col: str = "AQI", title: str = "Pollution Map"):
    """
    Simple scatter map using matplotlib (lat/lon).
    For interactive maps use plot_folium_map() with folium.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(df[lon_col], df[lat_col], c=df[value_col],
                    cmap="YlOrRd", alpha=0.7, s=50, edgecolors="none")
    plt.colorbar(sc, ax=ax, label=value_col)
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.tight_layout()
    return fig

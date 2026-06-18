"""
Main pipeline entry point.
Runs the full AI environmental chemistry workflow:
  1. Load data
  2. Preprocess
  3. Train pollution predictor
  4. Run remediation advisor
  5. Generate report figures
"""
from src.data.loader import load_sample_air_quality, load_sample_water_quality
from src.data.preprocessor import (
    clean_air_quality, engineer_air_features,
    build_numeric_pipeline, encode_categoricals, split_features_target
)
from src.models.pollution_predictor import PollutionPredictor
from src.models.remediation_advisor import RemediationAdvisor
from src.visualization.plots import (
    plot_aqi_trend, plot_correlation_heatmap,
    plot_feature_importance, plot_actual_vs_predicted
)
import matplotlib.pyplot as plt
import os


OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_air_quality_pipeline():
    print("=" * 60)
    print("  AI Environmental Chemistry — Air Quality Pipeline")
    print("=" * 60)

    # 1. Load data
    df = load_sample_air_quality()
    print(f"[1] Loaded air quality data: {df.shape[0]} rows, {df.shape[1]} columns")

    # 2. Preprocess
    df = clean_air_quality(df)
    df = engineer_air_features(df)
    df = encode_categoricals(df, columns=["location", "season", "pollution_level"])
    print("[2] Preprocessing complete.")

    # 3. Train AQI predictor
    feature_cols = ["PM2_5", "PM10", "NO2", "O3", "CO",
                    "temperature_C", "humidity_pct", "wind_speed_ms",
                    "month", "day_of_week", "heat_stagnation"]
    feature_cols = [c for c in feature_cols if c in df.columns]
    X, y = split_features_target(df, target="AQI", drop_cols=["date"])

    # Keep only numeric feature columns
    X = X[[c for c in feature_cols if c in X.columns]]

    predictor = PollutionPredictor(model_type="xgboost")
    metrics = predictor.train(X, y)
    print(f"[3] Predictor trained — MAE: {metrics['MAE']}, R2: {metrics['R2']}")

    # 4. Feature importance plot
    importances = predictor.feature_importances(list(X.columns))
    fig = plot_feature_importance(importances, title="AQI Prediction — Feature Importances")
    fig.savefig(os.path.join(OUTPUT_DIR, "feature_importance.png"), dpi=150)
    plt.close(fig)

    # 5. Actual vs predicted
    y_pred = predictor.predict(X)
    fig = plot_actual_vs_predicted(y.values, y_pred, label="AQI")
    fig.savefig(os.path.join(OUTPUT_DIR, "actual_vs_predicted.png"), dpi=150)
    plt.close(fig)

    # 6. Correlation heatmap
    fig = plot_correlation_heatmap(df[feature_cols + ["AQI"]])
    fig.savefig(os.path.join(OUTPUT_DIR, "correlation_heatmap.png"), dpi=150)
    plt.close(fig)

    print(f"[4] Charts saved to '{OUTPUT_DIR}/'")

    # 7. Rule-based remediation recommendation
    sample = {"PM2_5": 120, "NO2": 90, "O3": 130}
    advisor = RemediationAdvisor()
    recommendations = advisor.rule_based_recommend(sample)
    print("\n[5] Remediation Recommendations for sample measurement:")
    for issue, actions in recommendations.items():
        print(f"\n  Issue: {issue}")
        for a in actions:
            print(f"    - {a}")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    run_air_quality_pipeline()

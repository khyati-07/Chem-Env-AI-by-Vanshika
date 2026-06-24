# AI in Environmental Chemistry
## Predicting Pollution and Developing Remediation Strategies

This project applies Machine Learning and Data Science techniques to:
- Predict pollutant concentrations in air, water, and soil
- Identify pollution sources and hotspots
- Recommend evidence-based remediation strategies

---

## Project Structure

```
ai-env-chemistry/
├── data/
│   ├── raw/            # Raw datasets (CSV, JSON, NetCDF)
│   └── processed/      # Cleaned and feature-engineered data
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_pollution_prediction.ipynb
│   └── 03_remediation_strategies.ipynb
├── src/
│   ├── data/           # Data loading and preprocessing
│   ├── models/         # ML models for prediction and remediation
│   ├── visualization/  # Plots, heatmaps, time-series charts
│   └── utils/          # Shared helpers
└── tests/              # Unit tests
```

---

## Key Use Cases

| Use Case | Method |
|---|---|
| Air quality index (AQI) prediction | Random Forest, XGBoost |
| Heavy metal contamination in water | Gradient Boosting, SVM |
| Soil pollution mapping | Kriging + ML hybrid |
| Remediation strategy recommendation | Rule-based + ML classifier |
| Anomaly detection in sensor data | Isolation Forest |

---

## Datasets

Recommended public datasets:
- [EPA Air Quality](https://www.epa.gov/outdoor-air-quality-data)
- [WHO Global Water Quality](https://www.who.int/data/gho)
- [OpenAQ](https://openaq.org/)
- [USGS National Water Information System](https://waterdata.usgs.gov)

---

## Setup

### Streamlit App (Interactive Web UI)

**Prerequisites:** Python 3.9 or higher — download from [python.org](https://www.python.org/downloads/)

```bash
# 1. Install dependencies
pip install -r requirements_streamlit.txt

# 2. Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at **http://localhost:8501**

### Tkinter App (Desktop GUI)

```bash
# No extra packages needed — tkinter comes with Python
python smart_pollution_app.py
```

### Original ML Pipeline

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run main pipeline
python src/main.py
```

---

## Technologies

- **Python 3.9+**
- **scikit-learn** — ML models
- **XGBoost** — Gradient boosting for regression/classification
- **pandas / numpy** — Data manipulation
- **matplotlib / seaborn / plotly** — Visualization
- **geopandas / folium** — Geospatial pollution mapping
- **Jupyter** — Interactive exploration

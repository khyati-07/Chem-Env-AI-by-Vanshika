"""
=============================================================================
AI in Environmental Chemistry — Pollution Predictor App
=============================================================================
Class XI Chemistry Project
Topic: Predicting Pollution and Developing Remediation Strategies

This app uses a simple rule-based AI system to:
1. Calculate Air Quality Index (AQI) from pollutant values
2. Predict pollution levels based on weather conditions
3. Suggest remediation strategies
4. Provide educational information about pollutants

Requirements: Python 3.x (No additional installation needed!)
Run: python pollution_predictor_app.py
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

# ============== DATA & KNOWLEDGE BASE ==============

POLLUTANT_INFO = {
    "PM2.5": {
        "name": "Particulate Matter (PM2.5)",
        "formula": "Particles < 2.5 µm diameter",
        "unit": "µg/m³",
        "sources": "Vehicle exhaust, crop burning, construction dust, industrial emissions",
        "effects": "Penetrates deep into lungs, causes respiratory diseases, heart attacks, reduces life expectancy",
        "safe_limit": "60 µg/m³ (Indian Standard) / 25 µg/m³ (WHO)",
        "india_fact": "Delhi's PM2.5 often exceeds 300 µg/m³ in winter — 12x the WHO safe limit!",
        "breakpoints": [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
                       (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)]
    },
    "NO2": {
        "name": "Nitrogen Dioxide (NO₂)",
        "formula": "NO₂",
        "unit": "µg/m³",
        "sources": "Vehicle emissions, thermal power plants, industrial combustion",
        "effects": "Lung inflammation, reduced immunity, forms smog and acid rain",
        "safe_limit": "80 µg/m³ (Indian Standard) / 40 µg/m³ (WHO)",
        "india_fact": "Traffic junctions in Delhi and Mumbai show NO₂ levels 3-4x above safe limits",
        "breakpoints": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200),
                       (181, 280, 201, 300), (281, 400, 301, 400), (401, 800, 401, 500)]
    },
    "SO2": {
        "name": "Sulphur Dioxide (SO₂)",
        "formula": "SO₂",
        "unit": "µg/m³",
        "sources": "Coal burning, thermal power plants, oil refineries",
        "effects": "Acid rain (damages Taj Mahal!), breathing difficulty, crop damage",
        "safe_limit": "80 µg/m³ (Indian Standard) / 40 µg/m³ (WHO)",
        "india_fact": "SO₂ from Mathura refinery caused yellowing of Taj Mahal's marble",
        "breakpoints": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200),
                       (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 2400, 401, 500)]
    },
    "CO": {
        "name": "Carbon Monoxide (CO)",
        "formula": "CO",
        "unit": "mg/m³",
        "sources": "Incomplete combustion of petrol/diesel, biomass burning",
        "effects": "Binds with haemoglobin (200x stronger than O₂), reduces oxygen supply, headaches",
        "safe_limit": "4 mg/m³ (Indian Standard) / 4 mg/m³ (WHO)",
        "india_fact": "Auto-rickshaws and old diesel vehicles are major CO sources in Indian cities",
        "breakpoints": [(0, 1, 0, 50), (1.1, 2, 51, 100), (2.1, 10, 101, 200),
                       (10.1, 17, 201, 300), (17.1, 34, 301, 400), (34.1, 50, 401, 500)]
    },
    "O3": {
        "name": "Ground-Level Ozone (O₃)",
        "formula": "O₃",
        "unit": "µg/m³",
        "sources": "NOT directly emitted! Formed when NO₂ + VOCs react in sunlight",
        "effects": "Chest pain, coughing, throat irritation, worsens asthma",
        "safe_limit": "100 µg/m³ (Indian Standard) / 100 µg/m³ (WHO)",
        "india_fact": "Ozone levels peak in Indian summer (March-June) due to intense sunlight",
        "breakpoints": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200),
                       (169, 208, 201, 300), (209, 748, 301, 400), (749, 1000, 401, 500)]
    }
}

AQI_CATEGORIES = {
    "Good": {"range": (0, 50), "color": "#009966", "advice": "Air quality is satisfactory. Enjoy outdoor activities!"},
    "Satisfactory": {"range": (51, 100), "color": "#ffde33", "advice": "Acceptable air quality. Sensitive people should limit prolonged outdoor exertion."},
    "Moderate": {"range": (101, 200), "color": "#ff9933", "advice": "Breathing discomfort for sensitive people. Reduce prolonged outdoor activities."},
    "Poor": {"range": (201, 300), "color": "#cc0033", "advice": "Breathing discomfort on prolonged exposure. Avoid outdoor exercise. Use masks."},
    "Very Poor": {"range": (301, 400), "color": "#660099", "advice": "Respiratory illness on prolonged exposure. Stay indoors. Use air purifiers."},
    "Severe": {"range": (401, 500), "color": "#7e0023", "advice": "EMERGENCY! Affects healthy people. Schools should close. Avoid ALL outdoor activity."}
}

INDIAN_CITIES_DATA = {
    "Delhi": {"PM2.5": 180, "NO2": 95, "SO2": 18, "CO": 3.5, "O3": 45, "temp": 22, "humidity": 65, "wind": 4},
    "Mumbai": {"PM2.5": 85, "NO2": 65, "SO2": 12, "CO": 2.1, "O3": 55, "temp": 28, "humidity": 75, "wind": 12},
    "Bengaluru": {"PM2.5": 55, "NO2": 45, "SO2": 8, "CO": 1.5, "O3": 40, "temp": 25, "humidity": 60, "wind": 8},
    "Kolkata": {"PM2.5": 110, "NO2": 72, "SO2": 15, "CO": 2.8, "O3": 50, "temp": 30, "humidity": 80, "wind": 6},
    "Kanpur": {"PM2.5": 200, "NO2": 88, "SO2": 22, "CO": 4.0, "O3": 48, "temp": 24, "humidity": 70, "wind": 3},
    "Varanasi": {"PM2.5": 170, "NO2": 78, "SO2": 20, "CO": 3.2, "O3": 42, "temp": 26, "humidity": 68, "wind": 5},
    "Lucknow": {"PM2.5": 160, "NO2": 82, "SO2": 19, "CO": 3.0, "O3": 44, "temp": 25, "humidity": 66, "wind": 4},
    "Chennai": {"PM2.5": 45, "NO2": 38, "SO2": 9, "CO": 1.2, "O3": 60, "temp": 32, "humidity": 78, "wind": 10},
}

REMEDIATION_STRATEGIES = {
    "Good": [
        "✓ Continue current practices",
        "✓ Plant more trees to maintain air quality",
        "✓ Use public transport to prevent future degradation"
    ],
    "Satisfactory": [
        "✓ Use public transport or carpool",
        "✓ Avoid burning waste",
        "✓ Maintain vehicles regularly for emission checks",
        "✓ Plant air-purifying plants (Aloe Vera, Spider Plant)"
    ],
    "Moderate": [
        "⚠ Reduce vehicle usage — use metro/bus",
        "⚠ Industries should check emission control devices",
        "⚠ Avoid outdoor exercise during peak hours (8-10 AM)",
        "⚠ Use indoor air purifying plants (Peace Lily, Snake Plant)",
        "⚠ Sprinkle water on roads to reduce dust"
    ],
    "Poor": [
        "⚠ Wear N95 masks outdoors",
        "⚠ Ban on firecrackers and open burning",
        "⚠ Odd-Even traffic scheme should be implemented",
        "⚠ Use air purifiers indoors",
        "⚠ Increase frequency of mechanical road sweeping",
        "⚠ Schools should reduce outdoor activities"
    ],
    "Very Poor": [
        "🚨 Stop all construction activities",
        "🚨 Close brick kilns and stone crushers",
        "🚨 Deploy anti-smog guns and water sprinklers",
        "🚨 Strictly enforce vehicular emission norms",
        "🚨 Work from home advisories",
        "🚨 Shut down coal-based power plants in city limits"
    ],
    "Severe": [
        "🚨🚨 EMERGENCY MEASURES:",
        "🚨 Close all schools and colleges",
        "🚨 Ban entry of trucks into the city",
        "🚨 Complete construction ban",
        "🚨 Declare public health emergency",
        "🚨 Activate smog towers at full capacity",
        "🚨 Free distribution of masks to public",
        "🚨 Artificial rain (cloud seeding) if possible"
    ]
}


# ============== AI/LOGIC FUNCTIONS ==============

def calculate_sub_index(concentration, breakpoints):
    """Calculate AQI sub-index for a pollutant using linear interpolation."""
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= concentration <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
            return round(aqi)
    return 500  # Beyond highest breakpoint


def calculate_aqi(pollutant_values):
    """Calculate overall AQI (maximum of all sub-indices — Indian standard)."""
    sub_indices = {}
    for pollutant, value in pollutant_values.items():
        if value is not None and pollutant in POLLUTANT_INFO:
            sub_index = calculate_sub_index(value, POLLUTANT_INFO[pollutant]["breakpoints"])
            sub_indices[pollutant] = sub_index

    if not sub_indices:
        return 0, "N/A", {}

    aqi = max(sub_indices.values())
    dominant = max(sub_indices, key=sub_indices.get)
    return aqi, dominant, sub_indices


def get_aqi_category(aqi):
    """Get AQI category name from value."""
    for category, info in AQI_CATEGORIES.items():
        if info["range"][0] <= aqi <= info["range"][1]:
            return category
    return "Severe"


def predict_pollution_ai(temperature, humidity, wind_speed, season, city_type):
    """
    Simple Rule-Based AI System for pollution prediction.
    Uses decision rules learned from patterns in Indian pollution data.
    """
    # Base pollution score
    score = 50

    # Temperature effect (cold = more pollution due to inversion)
    if temperature < 15:
        score += 80
    elif temperature < 20:
        score += 50
    elif temperature < 25:
        score += 20
    elif temperature > 35:
        score += 15  # High temp = more ozone formation

    # Humidity effect (high humidity traps pollutants)
    if humidity > 80:
        score += 40
    elif humidity > 60:
        score += 20

    # Wind effect (high wind disperses pollutants)
    if wind_speed < 5:
        score += 60
    elif wind_speed < 10:
        score += 20
    elif wind_speed > 20:
        score -= 30

    # Season effect
    season_scores = {
        "Winter (Nov-Feb)": 80,
        "Summer (Mar-Jun)": 20,
        "Monsoon (Jul-Sep)": -20,  # Rain washes pollutants
        "Post-Monsoon (Oct-Nov)": 60  # Crop burning + Diwali
    }
    score += season_scores.get(season, 0)

    # City type effect
    city_scores = {
        "Metro (Delhi/Mumbai type)": 60,
        "Industrial City": 70,
        "Tier-2 City": 30,
        "Rural Area": -20
    }
    score += city_scores.get(city_type, 0)

    # Normalize to AQI range (0-500)
    predicted_aqi = max(0, min(500, score))

    return predicted_aqi


# ============== GUI APPLICATION ==============

class PollutionPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 AI Pollution Predictor — Class XI Chemistry Project")
        self.root.geometry("900x650")
        self.root.configure(bg="#f0f4f8")

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f4f8')
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), background='#f0f4f8')
        style.configure('Info.TLabel', font=('Arial', 10), background='#f0f4f8', wraplength=750)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_aqi_calculator_tab()
        self.create_prediction_tab()
        self.create_city_comparison_tab()
        self.create_learn_tab()

    def create_aqi_calculator_tab(self):
        """Tab 1: AQI Calculator — Input pollutant values and get AQI."""
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="📊 AQI Calculator")

        ttk.Label(frame, text="Air Quality Index (AQI) Calculator",
                  style='Title.TLabel').grid(row=0, column=0, columnspan=4, pady=(0, 5))
        ttk.Label(frame, text="Enter pollutant concentrations to calculate AQI (Indian Standard)",
                  style='Info.TLabel').grid(row=1, column=0, columnspan=4, pady=(0, 15))

        # Input fields
        self.pollutant_entries = {}
        row = 2
        for i, (key, info) in enumerate(POLLUTANT_INFO.items()):
            col = (i % 2) * 2
            if i > 0 and i % 2 == 0:
                row += 1

            ttk.Label(frame, text=f"{info['name']} ({info['unit']}):").grid(
                row=row, column=col, sticky='w', padx=5, pady=3)
            entry = ttk.Entry(frame, width=12)
            entry.grid(row=row, column=col + 1, padx=5, pady=3)
            entry.insert(0, "0")
            self.pollutant_entries[key] = entry

        row += 2
        # Quick fill button
        ttk.Button(frame, text="📋 Fill Sample Data (Delhi Winter)",
                   command=self.fill_sample_data).grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="🔍 Calculate AQI",
                   command=self.calculate_aqi_gui).grid(row=row, column=2, columnspan=2, pady=10)

        # Result area
        row += 1
        self.aqi_result_frame = ttk.LabelFrame(frame, text="Results", padding=10)
        self.aqi_result_frame.grid(row=row, column=0, columnspan=4, sticky='ew', pady=10)

        self.aqi_result_label = tk.Label(self.aqi_result_frame, text="Enter values and click Calculate",
                                         font=('Arial', 12), bg='white', pady=10, padx=10)
        self.aqi_result_label.pack(fill='x')

        self.remediation_text = tk.Text(self.aqi_result_frame, height=8, width=80, wrap='word',
                                        font=('Arial', 10))
        self.remediation_text.pack(fill='both', expand=True, pady=5)

    def create_prediction_tab(self):
        """Tab 2: AI Prediction — Predict pollution based on conditions."""
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="🤖 AI Prediction")

        ttk.Label(frame, text="AI-Based Pollution Prediction",
                  style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 5))
        ttk.Label(frame, text="Our AI uses weather conditions and location data to predict air quality",
                  style='Info.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 15))

        # Input fields
        ttk.Label(frame, text="Temperature (°C):").grid(row=2, column=0, sticky='w', pady=5)
        self.temp_entry = ttk.Entry(frame, width=15)
        self.temp_entry.grid(row=2, column=1, sticky='w', pady=5)
        self.temp_entry.insert(0, "18")

        ttk.Label(frame, text="Humidity (%):").grid(row=3, column=0, sticky='w', pady=5)
        self.humidity_entry = ttk.Entry(frame, width=15)
        self.humidity_entry.grid(row=3, column=1, sticky='w', pady=5)
        self.humidity_entry.insert(0, "70")

        ttk.Label(frame, text="Wind Speed (km/h):").grid(row=4, column=0, sticky='w', pady=5)
        self.wind_entry = ttk.Entry(frame, width=15)
        self.wind_entry.grid(row=4, column=1, sticky='w', pady=5)
        self.wind_entry.insert(0, "5")

        ttk.Label(frame, text="Season:").grid(row=5, column=0, sticky='w', pady=5)
        self.season_var = tk.StringVar(value="Winter (Nov-Feb)")
        seasons = ["Winter (Nov-Feb)", "Summer (Mar-Jun)", "Monsoon (Jul-Sep)", "Post-Monsoon (Oct-Nov)"]
        ttk.Combobox(frame, textvariable=self.season_var, values=seasons, width=25,
                     state='readonly').grid(row=5, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="City Type:").grid(row=6, column=0, sticky='w', pady=5)
        self.city_var = tk.StringVar(value="Metro (Delhi/Mumbai type)")
        cities = ["Metro (Delhi/Mumbai type)", "Industrial City", "Tier-2 City", "Rural Area"]
        ttk.Combobox(frame, textvariable=self.city_var, values=cities, width=25,
                     state='readonly').grid(row=6, column=1, sticky='w', pady=5)

        ttk.Button(frame, text="🤖 Predict Pollution Level",
                   command=self.predict_pollution_gui).grid(row=7, column=0, columnspan=2, pady=15)

        # Result area
        self.prediction_result_frame = ttk.LabelFrame(frame, text="AI Prediction Result", padding=10)
        self.prediction_result_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=5)

        self.prediction_label = tk.Label(self.prediction_result_frame,
                                         text="Set conditions and click Predict",
                                         font=('Arial', 12), bg='white', pady=10, padx=10)
        self.prediction_label.pack(fill='x')

        self.prediction_text = tk.Text(self.prediction_result_frame, height=8, width=70, wrap='word',
                                       font=('Arial', 10))
        self.prediction_text.pack(fill='both', expand=True, pady=5)

    def create_city_comparison_tab(self):
        """Tab 3: Compare Indian Cities."""
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="🏙️ Indian Cities")

        ttk.Label(frame, text="Pollution Comparison — Indian Cities",
                  style='Title.TLabel').pack(pady=(0, 5))
        ttk.Label(frame, text="Real-world approximate pollution data for major Indian cities",
                  style='Info.TLabel').pack(pady=(0, 10))

        # Create treeview (table)
        columns = ("City", "PM2.5", "NO₂", "SO₂", "CO", "O₃", "AQI", "Category")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        tree.column("City", width=120, anchor='w')
        tree.column("Category", width=120, anchor='center')

        for city, data in INDIAN_CITIES_DATA.items():
            pollutant_vals = {k: v for k, v in data.items() if k in POLLUTANT_INFO}
            aqi, dominant, _ = calculate_aqi(pollutant_vals)
            category = get_aqi_category(aqi)
            tree.insert('', 'end', values=(
                city, data["PM2.5"], data["NO2"], data["SO2"],
                data["CO"], data["O3"], aqi, category
            ))

        tree.pack(fill='both', expand=True, pady=5)

        # Info panel
        info_frame = ttk.LabelFrame(frame, text="Key Observations", padding=10)
        info_frame.pack(fill='x', pady=10)

        observations = (
            "🔴 Delhi & Kanpur have the worst air quality — PM2.5 is the dominant pollutant\n"
            "🟡 Mumbai & Kolkata are moderate due to sea breeze and monsoon patterns\n"
            "🟢 Chennai & Bengaluru have relatively better air due to coastal winds and greenery\n"
            "📊 In India, PM2.5 is almost always the dominant pollutant (unlike Western countries where O₃ dominates)\n"
            "🌬️ Wind speed is the single most important factor — notice how cities with higher wind have lower AQI"
        )
        ttk.Label(info_frame, text=observations, style='Info.TLabel', justify='left').pack()

    def create_learn_tab(self):
        """Tab 4: Learn about pollutants."""
        frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(frame, text="📚 Learn")

        ttk.Label(frame, text="Learn About Air Pollutants",
                  style='Title.TLabel').pack(pady=(0, 10))

        # Pollutant selector
        selector_frame = ttk.Frame(frame)
        selector_frame.pack(fill='x', pady=5)

        ttk.Label(selector_frame, text="Select Pollutant:").pack(side='left', padx=5)
        self.learn_var = tk.StringVar(value="PM2.5")
        pollutant_names = list(POLLUTANT_INFO.keys())
        combo = ttk.Combobox(selector_frame, textvariable=self.learn_var, values=pollutant_names,
                             width=20, state='readonly')
        combo.pack(side='left', padx=5)
        combo.bind('<<ComboboxSelected>>', self.show_pollutant_info)

        # Info display
        self.learn_text = tk.Text(frame, height=20, width=85, wrap='word', font=('Arial', 11),
                                  bg='#fffff0', padx=10, pady=10)
        self.learn_text.pack(fill='both', expand=True, pady=10)

        # Show default
        self.show_pollutant_info(None)

    # ============== EVENT HANDLERS ==============

    def fill_sample_data(self):
        """Fill sample data for Delhi winter conditions."""
        sample = {"PM2.5": "250", "NO2": "120", "SO2": "25", "CO": "4.5", "O3": "35"}
        for key, value in sample.items():
            self.pollutant_entries[key].delete(0, tk.END)
            self.pollutant_entries[key].insert(0, value)

    def calculate_aqi_gui(self):
        """Calculate AQI from entered values."""
        try:
            values = {}
            for key, entry in self.pollutant_entries.items():
                val = entry.get().strip()
                if val:
                    values[key] = float(val)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all pollutant concentrations!")
            return

        aqi, dominant, sub_indices = calculate_aqi(values)
        category = get_aqi_category(aqi)
        cat_info = AQI_CATEGORIES[category]

        # Update result label
        self.aqi_result_label.config(
            text=f"AQI = {aqi}  |  Category: {category}  |  Dominant Pollutant: {POLLUTANT_INFO[dominant]['name']}",
            bg=cat_info['color'],
            fg='white' if aqi > 100 else 'black'
        )

        # Show sub-indices and remediation
        self.remediation_text.delete('1.0', tk.END)
        self.remediation_text.insert(tk.END, "── Sub-Indices ──\n")
        for pollutant, sub_aqi in sub_indices.items():
            self.remediation_text.insert(tk.END, f"  {POLLUTANT_INFO[pollutant]['name']}: {sub_aqi}\n")

        self.remediation_text.insert(tk.END, f"\n── Health Advisory ──\n  {cat_info['advice']}\n")
        self.remediation_text.insert(tk.END, f"\n── AI-Recommended Remediation Strategies ──\n")
        for strategy in REMEDIATION_STRATEGIES[category]:
            self.remediation_text.insert(tk.END, f"  {strategy}\n")

    def predict_pollution_gui(self):
        """Run AI prediction based on weather conditions."""
        try:
            temp = float(self.temp_entry.get())
            humidity = float(self.humidity_entry.get())
            wind = float(self.wind_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperature, humidity, and wind speed!")
            return

        season = self.season_var.get()
        city_type = self.city_var.get()

        predicted_aqi = predict_pollution_ai(temp, humidity, wind, season, city_type)
        category = get_aqi_category(predicted_aqi)
        cat_info = AQI_CATEGORIES[category]

        self.prediction_label.config(
            text=f"Predicted AQI = {predicted_aqi}  |  Category: {category}",
            bg=cat_info['color'],
            fg='white' if predicted_aqi > 100 else 'black'
        )

        self.prediction_text.delete('1.0', tk.END)
        self.prediction_text.insert(tk.END, "── AI Analysis ──\n\n")

        # Explain the reasoning
        self.prediction_text.insert(tk.END, "Factors considered by our AI:\n\n")

        if temp < 15:
            self.prediction_text.insert(tk.END, "  🌡️ LOW TEMPERATURE: Cold weather causes temperature inversion,\n")
            self.prediction_text.insert(tk.END, "     trapping pollutants near the ground (major factor in Delhi winters)\n\n")
        elif temp < 20:
            self.prediction_text.insert(tk.END, "  🌡️ Cool temperature: Moderate inversion effect\n\n")
        else:
            self.prediction_text.insert(tk.END, "  🌡️ Warm temperature: Good vertical mixing of air\n\n")

        if wind < 5:
            self.prediction_text.insert(tk.END, "  🌬️ VERY LOW WIND: Pollutants cannot disperse! (Critical factor)\n\n")
        elif wind > 15:
            self.prediction_text.insert(tk.END, "  🌬️ Strong winds: Excellent pollutant dispersal\n\n")

        if humidity > 80:
            self.prediction_text.insert(tk.END, "  💧 HIGH HUMIDITY: Moisture traps particles, forms secondary pollutants\n\n")

        if "Winter" in season:
            self.prediction_text.insert(tk.END, "  ❄️ WINTER SEASON: Crop burning + low mixing height + festivals\n\n")
        elif "Monsoon" in season:
            self.prediction_text.insert(tk.END, "  🌧️ MONSOON: Rain washes out pollutants (natural cleansing!)\n\n")

        self.prediction_text.insert(tk.END, f"\n── Recommended Actions for {category} AQI ──\n\n")
        for strategy in REMEDIATION_STRATEGIES[category]:
            self.prediction_text.insert(tk.END, f"  {strategy}\n")

    def show_pollutant_info(self, event):
        """Display information about selected pollutant."""
        pollutant = self.learn_var.get()
        info = POLLUTANT_INFO[pollutant]

        self.learn_text.delete('1.0', tk.END)
        self.learn_text.insert(tk.END, f"{'═' * 60}\n")
        self.learn_text.insert(tk.END, f"  {info['name']}\n")
        self.learn_text.insert(tk.END, f"{'═' * 60}\n\n")

        self.learn_text.insert(tk.END, f"📋 Chemical Formula/Description:\n   {info['formula']}\n\n")
        self.learn_text.insert(tk.END, f"📏 Unit of Measurement:\n   {info['unit']}\n\n")
        self.learn_text.insert(tk.END, f"🏭 Sources:\n   {info['sources']}\n\n")
        self.learn_text.insert(tk.END, f"⚠️ Health Effects:\n   {info['effects']}\n\n")
        self.learn_text.insert(tk.END, f"✅ Safe Limit:\n   {info['safe_limit']}\n\n")
        self.learn_text.insert(tk.END, f"🇮🇳 India Fact:\n   {info['india_fact']}\n\n")

        # Add chemistry
        self.learn_text.insert(tk.END, f"{'─' * 60}\n")
        self.learn_text.insert(tk.END, f"🧪 Related Chemical Reactions:\n\n")

        if pollutant == "PM2.5":
            self.learn_text.insert(tk.END, "   Crop Burning Reaction:\n")
            self.learn_text.insert(tk.END, "   CₓHᵧ + O₂ → CO₂ + H₂O + PM (incomplete combustion)\n\n")
            self.learn_text.insert(tk.END, "   Secondary PM formation:\n")
            self.learn_text.insert(tk.END, "   SO₂ + NH₃ + H₂O → (NH₄)₂SO₄ (particulate)\n")
        elif pollutant == "NO2":
            self.learn_text.insert(tk.END, "   In vehicle engines (high temperature):\n")
            self.learn_text.insert(tk.END, "   N₂ + O₂ → 2NO (at >1000°C)\n")
            self.learn_text.insert(tk.END, "   2NO + O₂ → 2NO₂\n\n")
            self.learn_text.insert(tk.END, "   Photochemical smog formation:\n")
            self.learn_text.insert(tk.END, "   NO₂ + sunlight → NO + O\n")
            self.learn_text.insert(tk.END, "   O + O₂ → O₃ (ground-level ozone)\n")
        elif pollutant == "SO2":
            self.learn_text.insert(tk.END, "   From coal burning:\n")
            self.learn_text.insert(tk.END, "   S + O₂ → SO₂\n\n")
            self.learn_text.insert(tk.END, "   Acid rain formation:\n")
            self.learn_text.insert(tk.END, "   2SO₂ + O₂ → 2SO₃\n")
            self.learn_text.insert(tk.END, "   SO₃ + H₂O → H₂SO₄\n\n")
            self.learn_text.insert(tk.END, "   Taj Mahal damage:\n")
            self.learn_text.insert(tk.END, "   CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂\n")
        elif pollutant == "CO":
            self.learn_text.insert(tk.END, "   Incomplete combustion:\n")
            self.learn_text.insert(tk.END, "   2C + O₂ → 2CO (limited oxygen)\n\n")
            self.learn_text.insert(tk.END, "   Poisoning mechanism:\n")
            self.learn_text.insert(tk.END, "   Hb + CO → HbCO (carboxyhemoglobin)\n")
            self.learn_text.insert(tk.END, "   (CO binds 200x more strongly than O₂!)\n")
        elif pollutant == "O3":
            self.learn_text.insert(tk.END, "   Ground-level ozone formation:\n")
            self.learn_text.insert(tk.END, "   NO₂ + hν → NO + O (UV light breaks NO₂)\n")
            self.learn_text.insert(tk.END, "   O + O₂ → O₃\n\n")
            self.learn_text.insert(tk.END, "   Stratospheric ozone (good ozone):\n")
            self.learn_text.insert(tk.END, "   O₂ + hν → 2O (UV-C breaks O₂)\n")
            self.learn_text.insert(tk.END, "   O + O₂ → O₃ (protects us from UV!)\n\n")
            self.learn_text.insert(tk.END, "   Ozone destruction by CFCs:\n")
            self.learn_text.insert(tk.END, "   CF₂Cl₂ + hν → Cl + CF₂Cl\n")
            self.learn_text.insert(tk.END, "   Cl + O₃ → ClO + O₂\n")
            self.learn_text.insert(tk.END, "   ClO + O → Cl + O₂ (Cl is regenerated!)\n")


# ============== MAIN ==============

if __name__ == "__main__":
    root = tk.Tk()
    app = PollutionPredictorApp(root)
    root.mainloop()

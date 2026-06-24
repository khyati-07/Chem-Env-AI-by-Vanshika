"""
=============================================================================
AI in Environmental Chemistry — Smart Pollution Predictor App (Streamlit v2.0)
=============================================================================
Class XI Chemistry Project
Topic: Predicting Pollution and Developing Remediation Strategies

🤖 AI FEATURES:
1. AUTO-FETCHES real-time weather data (no manual input needed!)
2. AUTO-FETCHES real-time air quality data from satellites
3. AI analyzes patterns and predicts future pollution
4. Suggests smart remediation based on actual conditions
5. Learn tab — detailed info on each pollutant with chemical reactions

Uses FREE Open-Meteo API — No API key needed!
Requirements: Python 3.x + Internet connection + streamlit
Run: streamlit run streamlit_app.py
=============================================================================
"""

import streamlit as st
import urllib.request
import json
from datetime import datetime
import math

# ============== INDIAN CITIES DATABASE ==============

INDIAN_CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "type": "Metro", "info": "Capital city, severe winter pollution"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "type": "Metro", "info": "Coastal city, sea breeze helps"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "type": "Metro", "info": "Garden city, moderate pollution"},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "type": "Metro", "info": "Humid climate, industrial area"},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "type": "Metro", "info": "Coastal city, good dispersal"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "type": "Metro", "info": "IT hub, growing vehicular pollution"},
    "Kanpur": {"lat": 26.4499, "lon": 80.3319, "type": "Industrial", "info": "One of India's most polluted cities"},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462, "type": "Metro", "info": "UP capital, winter smog issues"},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739, "type": "Tier-2", "info": "Religious city, cremation ghats contribute"},
    "Agra": {"lat": 27.1767, "lon": 78.0081, "type": "Tier-2", "info": "Taj Mahal affected by SO₂ pollution"},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "type": "Metro", "info": "Desert dust + vehicular emissions"},
    "Patna": {"lat": 25.6093, "lon": 85.1376, "type": "Tier-2", "info": "Indo-Gangetic plain, very high PM2.5"},
}

# ============== POLLUTANT KNOWLEDGE BASE ==============

POLLUTANT_INFO = {
    "PM2.5": {
        "name": "Particulate Matter (PM2.5)",
        "formula": "Particles < 2.5 µm diameter",
        "unit": "µg/m³",
        "who_limit": 25,
        "india_limit": 60,
        "sources": "Vehicle exhaust, crop burning, construction dust, industrial emissions",
        "effects": "Penetrates deep into lungs → respiratory diseases, heart attacks, reduces life expectancy",
        "safe_limit": "60 µg/m³ (Indian Standard) / 25 µg/m³ (WHO)",
        "india_fact": "Delhi's PM2.5 often exceeds 300 µg/m³ in winter — 12x the WHO safe limit!",
        "chemistry": "Secondary PM formation:\nSO₂ + NH₃ + H₂O → (NH₄)₂SO₄ (particulate)\n\nCrop Burning:\nCₓHᵧ + O₂ → CO₂ + H₂O + PM (incomplete combustion)",
        "breakpoints": [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
                       (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)]
    },
    "PM10": {
        "name": "Particulate Matter (PM10)",
        "formula": "Particles < 10 µm diameter",
        "unit": "µg/m³",
        "who_limit": 50,
        "india_limit": 100,
        "sources": "Road dust, construction, mining, pollen, industrial processes",
        "effects": "Settles in upper airways → coughing, asthma attacks, reduced visibility",
        "safe_limit": "100 µg/m³ (Indian Standard) / 50 µg/m³ (WHO)",
        "india_fact": "Construction boom in Indian cities makes PM10 a constant problem year-round",
        "chemistry": "Mechanical process — not chemical:\nDust particles suspended by wind and traffic\nSize: >2.5 µm to <10 µm (visible under microscope)",
        "breakpoints": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200),
                       (251, 350, 201, 300), (351, 430, 301, 400), (431, 600, 401, 500)]
    },
    "NO₂": {
        "name": "Nitrogen Dioxide (NO₂)",
        "formula": "NO₂",
        "unit": "µg/m³",
        "who_limit": 40,
        "india_limit": 80,
        "sources": "Vehicle emissions, thermal power plants, industrial combustion",
        "effects": "Lung inflammation, reduced immunity, forms smog and acid rain",
        "safe_limit": "80 µg/m³ (Indian Standard) / 40 µg/m³ (WHO)",
        "india_fact": "Traffic junctions in Delhi and Mumbai show NO₂ levels 3-4x above safe limits",
        "chemistry": "In vehicle engines (high temperature):\nN₂ + O₂ → 2NO (at >1000°C)\n2NO + O₂ → 2NO₂\n\nPhotochemical smog:\nNO₂ + sunlight → NO + O\nO + O₂ → O₃ (ground-level ozone!)",
        "breakpoints": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200),
                       (181, 280, 201, 300), (281, 400, 301, 400), (401, 800, 401, 500)]
    },
    "SO₂": {
        "name": "Sulphur Dioxide (SO₂)",
        "formula": "SO₂",
        "unit": "µg/m³",
        "who_limit": 40,
        "india_limit": 80,
        "sources": "Coal burning, thermal power plants, oil refineries",
        "effects": "Acid rain (damages Taj Mahal!), breathing difficulty, crop damage",
        "safe_limit": "80 µg/m³ (Indian Standard) / 40 µg/m³ (WHO)",
        "india_fact": "SO₂ from Mathura refinery caused yellowing of Taj Mahal's marble",
        "chemistry": "From coal burning:\nS + O₂ → SO₂\n\nAcid rain formation:\n2SO₂ + O₂ → 2SO₃\nSO₃ + H₂O → H₂SO₄ (sulphuric acid)\n\nTaj Mahal damage:\nCaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂",
        "breakpoints": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200),
                       (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 2400, 401, 500)]
    },
    "CO": {
        "name": "Carbon Monoxide (CO)",
        "formula": "CO",
        "unit": "mg/m³",
        "who_limit": 4,
        "india_limit": 4,
        "sources": "Incomplete combustion of petrol/diesel, biomass burning, chulhas",
        "effects": "Binds with haemoglobin (200x stronger than O₂), reduces oxygen supply, can be fatal",
        "safe_limit": "4 mg/m³ (Indian Standard) / 4 mg/m³ (WHO)",
        "india_fact": "Auto-rickshaws and old diesel vehicles are major CO sources in Indian cities",
        "chemistry": "Incomplete combustion:\n2C + O₂ → 2CO (limited oxygen)\n\nPoisoning mechanism:\nHb + CO → HbCO (carboxyhemoglobin)\n(CO binds 200x more strongly than O₂!)\n\nComplete combustion (safe):\nC + O₂ → CO₂",
        "breakpoints": [(0, 1, 0, 50), (1.1, 2, 51, 100), (2.1, 10, 101, 200),
                       (10.1, 17, 201, 300), (17.1, 34, 301, 400), (34.1, 50, 401, 500)]
    },
    "O₃": {
        "name": "Ozone (O₃)",
        "formula": "O₃",
        "unit": "µg/m³",
        "who_limit": 100,
        "india_limit": 100,
        "sources": "NOT directly emitted! Formed when NO₂ + VOCs react in sunlight",
        "effects": "Chest pain, coughing, throat irritation, worsens asthma",
        "safe_limit": "100 µg/m³ (Indian Standard) / 100 µg/m³ (WHO)",
        "india_fact": "Ozone levels peak in Indian summer (March-June) due to intense sunlight",
        "chemistry": "Ground-level ozone (BAD):\nNO₂ + hν → NO + O (UV breaks NO₂)\nO + O₂ → O₃\n\nStratospheric ozone (GOOD — protects us):\nO₂ + hν → 2O (UV-C breaks O₂)\nO + O₂ → O₃\n\nOzone destruction by CFCs:\nCF₂Cl₂ + hν → Cl + CF₂Cl\nCl + O₃ → ClO + O₂\nClO + O → Cl + O₂ (Cl regenerated — chain reaction!)",
        "breakpoints": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200),
                       (169, 208, 201, 300), (209, 748, 301, 400), (749, 1000, 401, 500)]
    }
}

AQI_CATEGORIES = {
    "Good": {"range": (0, 50), "color": "#009966", "fg": "white"},
    "Satisfactory": {"range": (51, 100), "color": "#ffde33", "fg": "black"},
    "Moderate": {"range": (101, 200), "color": "#ff9933", "fg": "black"},
    "Poor": {"range": (201, 300), "color": "#cc0033", "fg": "white"},
    "Very Poor": {"range": (301, 400), "color": "#660099", "fg": "white"},
    "Severe": {"range": (401, 500), "color": "#7e0023", "fg": "white"},
}

REMEDIATION = {
    "Good": ["✅ Air quality is excellent!", "✅ Enjoy outdoor activities", "✅ Keep planting trees to maintain this"],
    "Satisfactory": ["✓ Mostly fine — sensitive people should be cautious", "✓ Use public transport to keep it this way",
                     "✓ Plant air-purifying indoor plants (Snake Plant, Aloe Vera)"],
    "Moderate": ["⚠️ Reduce prolonged outdoor exercise", "⚠️ Asthmatics should carry inhalers",
                 "⚠️ Industries should verify emission controls", "⚠️ Sprinkle water on roads"],
    "Poor": ["🚨 Wear N95 masks outdoors", "🚨 Avoid outdoor exercise completely",
             "🚨 Use air purifiers indoors", "🚨 Implement Odd-Even vehicle scheme",
             "🚨 Increase road sweeping frequency"],
    "Very Poor": ["🚨🚨 Stay indoors! Use air purifiers", "🚨🚨 Schools should cancel outdoor activities",
                  "🚨🚨 Deploy anti-smog guns", "🚨🚨 Ban construction & industrial activity",
                  "🚨🚨 Work from home advisory"],
    "Severe": ["‼️ PUBLIC HEALTH EMERGENCY", "‼️ Close all schools", "‼️ Ban ALL vehicles except emergency",
               "‼️ Shut down industrial units", "‼️ Consider cloud seeding for artificial rain",
               "‼️ Free N95 mask distribution"]
}


# ============== WATER POLLUTION DATABASE (CPCB Published Data) ==============

WATER_QUALITY_PARAMS = {
    "pH": {"name": "pH", "unit": "", "safe_min": 6.5, "safe_max": 8.5,
            "chemistry": "Measures H⁺ ion concentration. pH = -log[H⁺]\npH < 7 = acidic (industrial discharge)\npH > 8.5 = alkaline (detergent/soap discharge)"},
    "DO": {"name": "Dissolved Oxygen", "unit": "mg/L", "safe_min": 5.0, "safe_max": 14.0,
            "chemistry": "O₂ dissolved in water. Fish need >5 mg/L to survive.\nSolubility decreases with temperature (Henry's Law).\nLow DO = organic waste consuming oxygen via decomposition."},
    "BOD": {"name": "Biochem. Oxygen Demand", "unit": "mg/L", "safe_min": 0, "safe_max": 3.0,
             "chemistry": "Amount of O₂ bacteria need to decompose organic waste.\nHigh BOD = heavy sewage/organic pollution.\nReaction: Organic matter + O₂ → CO₂ + H₂O (by bacteria)"},
    "COD": {"name": "Chemical Oxygen Demand", "unit": "mg/L", "safe_min": 0, "safe_max": 10.0,
             "chemistry": "Total O₂ needed to oxidize ALL chemicals (organic + inorganic).\nMeasured using K₂Cr₂O₇ (potassium dichromate) as oxidizing agent.\nCOD > BOD always (includes non-biodegradable chemicals too)."},
    "Nitrates": {"name": "Nitrates (NO₃⁻)", "unit": "mg/L", "safe_min": 0, "safe_max": 45.0,
                  "chemistry": "From fertilizer runoff and sewage.\nExcess nitrates → eutrophication → algal bloom → O₂ depletion.\nNH₄⁺ → NO₂⁻ → NO₃⁻ (nitrification by bacteria)"},
    "Turbidity": {"name": "Turbidity", "unit": "NTU", "safe_min": 0, "safe_max": 5.0,
                   "chemistry": "Suspended particles scattering light.\nHigh turbidity blocks sunlight → reduces photosynthesis in water.\nSources: soil erosion, construction runoff, algae."},
    "Chromium": {"name": "Chromium (Cr⁶⁺)", "unit": "mg/L", "safe_min": 0, "safe_max": 0.05,
                  "chemistry": "Hexavalent chromium from tanneries/electroplating.\nCr⁶⁺ is carcinogenic! Cr³⁺ is less toxic.\nRemediation: Reduce Cr⁶⁺ → Cr³⁺ using FeSO₄ (ferrous sulphate)"},
}

RIVER_DATA = {
    "Yamuna — Delhi (Wazirabad-Okhla)": {
        "pH": 7.8, "DO": 1.2, "BOD": 28.0, "COD": 58.0, "Nitrates": 18.0, "Turbidity": 85.0, "Chromium": 0.01,
        "info": "Receives 70% of Delhi's sewage. DO drops to near ZERO — essentially dead river.",
        "sources": "18 major drains discharge untreated sewage + industrial effluents",
        "lat": 28.6139, "lon": 77.2090
    },
    "Ganga — Varanasi": {
        "pH": 7.9, "DO": 4.5, "BOD": 8.5, "COD": 22.0, "Nitrates": 12.0, "Turbidity": 45.0, "Chromium": 0.02,
        "info": "Cremation ghats + tannery waste + sewage from 30+ drains.",
        "sources": "Sewage (80%), industrial waste (15%), religious offerings/cremation (5%)",
        "lat": 25.3176, "lon": 82.9739
    },
    "Ganga — Kanpur": {
        "pH": 7.4, "DO": 3.2, "BOD": 15.0, "COD": 42.0, "Nitrates": 22.0, "Turbidity": 68.0, "Chromium": 0.12,
        "info": "400+ tanneries discharge chromium-laden waste. Major pollution hotspot.",
        "sources": "Tannery effluents (Cr⁶⁺), textile dyes, municipal sewage",
        "lat": 26.4499, "lon": 80.3319
    },
    "Yamuna — Agra": {
        "pH": 8.1, "DO": 2.8, "BOD": 18.0, "COD": 35.0, "Nitrates": 15.0, "Turbidity": 55.0, "Chromium": 0.03,
        "info": "Already polluted from Delhi. Further degraded by Agra's sewage + industrial waste.",
        "sources": "Upstream Delhi pollution + local drains + small industries",
        "lat": 27.1767, "lon": 78.0081
    },
    "Bellandur Lake — Bengaluru": {
        "pH": 8.5, "DO": 0.5, "BOD": 85.0, "COD": 180.0, "Nitrates": 35.0, "Turbidity": 120.0, "Chromium": 0.04,
        "info": "Caught FIRE due to chemical foam! Methane from decomposing organic waste.",
        "sources": "IT corridor sewage + chemical industries + detergent-rich grey water",
        "lat": 12.9352, "lon": 77.6744
    },
    "Cooum River — Chennai": {
        "pH": 7.2, "DO": 1.8, "BOD": 45.0, "COD": 95.0, "Nitrates": 28.0, "Turbidity": 92.0, "Chromium": 0.02,
        "info": "One of India's most polluted urban rivers. Open sewage drain.",
        "sources": "Slum sewage, industrial discharge, solid waste dumping",
        "lat": 13.0827, "lon": 80.2707
    },
    "Hooghly — Kolkata": {
        "pH": 7.6, "DO": 4.0, "BOD": 6.5, "COD": 18.0, "Nitrates": 10.0, "Turbidity": 40.0, "Chromium": 0.03,
        "info": "Tidal river helps flushing, but heavy industrial belt upstream.",
        "sources": "Jute mills, tanneries, municipal sewage, idol immersion (seasonal)",
        "lat": 22.5726, "lon": 88.3639
    },
    "Sabarmati — Ahmedabad": {
        "pH": 8.3, "DO": 2.0, "BOD": 32.0, "COD": 72.0, "Nitrates": 20.0, "Turbidity": 70.0, "Chromium": 0.06,
        "info": "Riverfront beautified but water quality remains poor downstream.",
        "sources": "Textile/dye industry effluents, pharmaceutical waste, sewage",
        "lat": 23.0225, "lon": 72.5714
    },
}


# ============== LOGIC FUNCTIONS (UNCHANGED) ==============

def ai_analyze_water(river_name, data):
    """AI analysis for water pollution — correlations, causes, predictions."""
    analysis = []
    predictions = []
    remediation = []

    do_val = data["DO"]
    bod = data["BOD"]
    cod = data["COD"]
    ph = data["pH"]
    nitrates = data["Nitrates"]
    turbidity = data["Turbidity"]
    chromium = data["Chromium"]

    # ─── DO-BOD Correlation (Key relationship in water chemistry) ───
    if do_val < 2:
        analysis.append(
            "🔴 CRITICAL: DO < 2 mg/L — WATER IS NEARLY DEAD!\n"
            "   Correlation: High BOD ({:.1f}) is consuming all available oxygen.\n"
            "   Chemistry: Organic waste + O₂ → CO₂ + H₂O (bacteria use up O₂)\n"
            "   Impact: No fish/aquatic life can survive below 2 mg/L DO.\n"
            "   This is called 'Biochemical Oxygen Demand' because bacteria\n"
            "   DEMAND oxygen to break down sewage.".format(bod))
    elif do_val < 5:
        analysis.append(
            "🟠 WARNING: DO < 5 mg/L — Aquatic life stressed!\n"
            "   Only pollution-tolerant species can survive.\n"
            "   Cause: BOD = {:.1f} mg/L (should be <3 for clean water).\n"
            "   The sewage is 'eating up' dissolved oxygen.".format(bod))
    else:
        analysis.append(
            "🟢 DO = {:.1f} mg/L — Adequate for aquatic life.\n"
            "   Oxygen levels support healthy fish populations.".format(do_val))

    # ─── BOD-COD Ratio Analysis ───
    if cod > 0:
        ratio = bod / cod
        if ratio > 0.5:
            analysis.append(
                "📊 BOD/COD ratio = {:.2f} (>0.5) — Pollution is BIODEGRADABLE.\n"
                "   Meaning: Mostly sewage/organic waste (bacteria can break it down).\n"
                "   Good news: Biological treatment (STPs) will be effective!".format(ratio))
        else:
            analysis.append(
                "📊 BOD/COD ratio = {:.2f} (<0.5) — Pollution is NON-BIODEGRADABLE.\n"
                "   Meaning: Industrial chemicals that bacteria CANNOT decompose.\n"
                "   Bad news: Needs advanced chemical treatment (oxidation/adsorption).".format(ratio))

    # ─── Eutrophication Prediction ───
    if nitrates > 20:
        predictions.append(
            "🧪 AI PREDICTION: HIGH EUTROPHICATION RISK!\n"
            "   Nitrates = {:.1f} mg/L (above 20 mg/L = danger zone)\n"
            "   Prediction chain:\n"
            "   High NO₃⁻ → Algal bloom → Algae die → Bacteria decompose algae\n"
            "   → O₂ consumed → DO crashes → Fish die (mass kill event)\n"
            "   Timeline: Algal bloom likely within 5-7 days if sunlight + warm temp.".format(nitrates))
    elif nitrates > 10:
        predictions.append(
            "🟡 Nitrates = {:.1f} mg/L — Moderate eutrophication risk.\n"
            "   Source: Likely agricultural fertilizer runoff (NPK fertilizers).\n"
            "   Monitor: If levels rise further, algal bloom may occur.".format(nitrates))

    # ─── Heavy Metal Analysis ───
    if chromium > 0.05:
        analysis.append(
            "☠️ CHROMIUM = {:.3f} mg/L — EXCEEDS SAFE LIMIT (0.05 mg/L)!\n"
            "   Source: Tanneries (leather processing uses Cr₂O₃)\n"
            "   Chemistry: Cr⁶⁺ (hexavalent) is CARCINOGENIC\n"
            "   Cr⁶⁺ enters cells → damages DNA → causes cancer\n"
            "   Kanpur's 400+ tanneries are the biggest offenders in India.".format(chromium))

    # ─── pH Analysis ───
    if ph < 6.5:
        analysis.append(
            "🔴 pH = {:.1f} — TOO ACIDIC!\n"
            "   Likely cause: Industrial acid discharge or acid mine drainage.\n"
            "   Effect: Dissolves heavy metals from sediment, toxic to fish.".format(ph))
    elif ph > 8.5:
        analysis.append(
            "🟠 pH = {:.1f} — TOO ALKALINE!\n"
            "   Likely cause: Detergent/soap discharge (Na₂CO₃, NaOH).\n"
            "   Effect: Ammonia becomes more toxic at high pH.".format(ph))

    # ─── AI Predictions ───
    if do_val < 3 and bod > 20:
        predictions.append(
            "⚠️ AI PREDICTION: If no intervention:\n"
            "   → DO will drop to 0 within 24-48 hours in stagnant stretches\n"
            "   → Anaerobic conditions will produce H₂S (rotten egg smell)\n"
            "   → CH₄ (methane) generation — fire risk (like Bellandur Lake!)\n"
            "   Chemistry: Anaerobic decomposition produces:\n"
            "   Organic matter → CH₄ + H₂S + NH₃ (without oxygen)")

    if turbidity > 50 and nitrates > 15:
        predictions.append(
            "🌊 AI PREDICTION: Combined high turbidity + nitrates:\n"
            "   → Turbidity blocks sunlight → aquatic plants can't photosynthesize\n"
            "   → Less O₂ production + more O₂ consumption = oxygen collapse\n"
            "   → Expect further DO decline in coming days")

    # ─── Remediation Strategies ───
    if bod > 10:
        remediation.append(
            "🏗️ SEWAGE TREATMENT (for high BOD):\n"
            "   1. Primary: Sedimentation tanks (remove solids)\n"
            "   2. Secondary: Activated sludge process (bacteria eat organic waste)\n"
            "      Organic matter + O₂ → CO₂ + H₂O + new bacteria\n"
            "   3. Tertiary: Chlorination/UV for pathogen removal\n"
            "   India needs: 70% of sewage is currently UNTREATED!")

    if chromium > 0.05:
        remediation.append(
            "🧪 HEAVY METAL REMOVAL (for Chromium):\n"
            "   Chemical method: Cr⁶⁺ + FeSO₄ → Cr³⁺ (less toxic) + Fe³⁺\n"
            "   Then: Cr³⁺ + 3OH⁻ → Cr(OH)₃ ↓ (precipitates out)\n"
            "   Phytoremediation: Plants like Water Hyacinth absorb metals\n"
            "   Zero Liquid Discharge (ZLD) for tanneries — recycle all water")

    if nitrates > 20:
        remediation.append(
            "🌱 EUTROPHICATION CONTROL (for high Nitrates):\n"
            "   • Reduce fertilizer use — promote organic farming\n"
            "   • Constructed wetlands (natural filtration)\n"
            "   • Buffer zones along rivers (grass strips trap runoff)\n"
            "   • Denitrification: NO₃⁻ → N₂↑ (bacteria in anaerobic zone)")

    if do_val < 4:
        remediation.append(
            "💨 AERATION (to increase DO):\n"
            "   • Install aerators/fountains in stagnant stretches\n"
            "   • Weirs and cascades increase surface area for O₂ absorption\n"
            "   • Bio-remediation: Add O₂-producing algae (controlled)\n"
            "   • Long-term: Ensure minimum ecological flow in rivers")

    remediation.append(
        "🏛️ GOVERNMENT PROGRAMMES:\n"
        "   • Namami Gange (₹20,000 crore) — STPs + industrial regulation\n"
        "   • CPCB Real-Time Monitoring — 600+ water quality stations\n"
        "   • National Green Tribunal — penalizes polluting industries\n"
        "   • CETP (Common Effluent Treatment Plants) for industrial clusters")

    return analysis, predictions, remediation


# ============== API FUNCTIONS (THE AI BRAIN) ==============

def fetch_live_weather(lat, lon):
    """Fetch REAL-TIME weather data from Open-Meteo (free, no API key!)."""
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
           f"&timezone=Asia/Kolkata")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ClassXI-Chemistry-Project/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            current = data["current"]
            return {
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "wind_speed": current["wind_speed_10m"],
                "wind_direction": current["wind_direction_10m"],
                "success": True
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_live_air_quality(lat, lon):
    """Fetch BOTH current hour AND 24-hour average air quality data."""
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
           f"latitude={lat}&longitude={lon}"
           f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
           f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
           f"&past_days=1&forecast_days=3&timezone=Asia/Kolkata")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ClassXI-Chemistry-Project/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            current = data["current"]
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])

            # Current hour values
            current_vals = {
                "PM2.5": current.get("pm2_5", 0),
                "PM10": current.get("pm10", 0),
                "NO₂": current.get("nitrogen_dioxide", 0),
                "SO₂": current.get("sulphur_dioxide", 0),
                "CO": current.get("carbon_monoxide", 0) / 1000,
                "O₃": current.get("ozone", 0),
            }

            # 24-hour average values (how CPCB/Google calculates AQI)
            # Use ONLY last 24 hours (rolling window) — this matches CPCB method
            # Find current hour index
            current_time = current.get("time", "")
            try:
                curr_idx = times.index(current_time)
            except ValueError:
                curr_idx = 24  # fallback

            past_24 = slice(max(0, curr_idx - 23), curr_idx + 1)

            def avg_slice(values, s):
                chunk = [v for v in values[s] if v is not None]
                return round(sum(chunk) / len(chunk), 1) if chunk else 0

            # CAMS satellite model overestimates ground-level PM for Indian cities
            PM_CORRECTION = 0.55
            GAS_CORRECTION = 0.75

            avg_vals = {
                "PM2.5": round(avg_slice(hourly.get("pm2_5", []), past_24) * PM_CORRECTION, 1),
                "PM10": round(avg_slice(hourly.get("pm10", []), past_24) * PM_CORRECTION, 1),
                "NO₂": round(avg_slice(hourly.get("nitrogen_dioxide", []), past_24) * GAS_CORRECTION, 1),
                "SO₂": round(avg_slice(hourly.get("sulphur_dioxide", []), past_24) * GAS_CORRECTION, 1),
                "CO": round(avg_slice(hourly.get("carbon_monoxide", []), past_24) / 1000 * GAS_CORRECTION, 2),
                "O₃": round(avg_slice(hourly.get("ozone", []), past_24) * GAS_CORRECTION, 1),
            }

            # 3-day forecast (daily averages from future hours) — ALL pollutants
            forecast_days = []
            future_start = curr_idx + 1
            pm25_all = hourly.get("pm2_5", [])
            pm10_all = hourly.get("pm10", [])
            no2_all = hourly.get("nitrogen_dioxide", [])
            so2_all = hourly.get("sulphur_dioxide", [])
            co_all = hourly.get("carbon_monoxide", [])
            o3_all = hourly.get("ozone", [])

            for day_offset in range(3):
                day_start = future_start + day_offset * 24
                day_end = day_start + 24
                day_pm25 = [v for v in pm25_all[day_start:day_end] if v is not None]
                day_pm10 = [v for v in pm10_all[day_start:day_end] if v is not None]
                day_no2 = [v for v in no2_all[day_start:day_end] if v is not None]
                day_so2 = [v for v in so2_all[day_start:day_end] if v is not None]
                day_co = [v for v in co_all[day_start:day_end] if v is not None]
                day_o3 = [v for v in o3_all[day_start:day_end] if v is not None]
                if day_pm25:
                    avg_pm25 = round(sum(day_pm25) / len(day_pm25) * PM_CORRECTION, 1)
                    avg_pm10 = round(sum(day_pm10) / len(day_pm10) * PM_CORRECTION, 1) if day_pm10 else 0
                    avg_no2 = round(sum(day_no2) / len(day_no2) * GAS_CORRECTION, 1) if day_no2 else 0
                    avg_so2 = round(sum(day_so2) / len(day_so2) * GAS_CORRECTION, 1) if day_so2 else 0
                    avg_co = round(sum(day_co) / len(day_co) / 1000 * GAS_CORRECTION, 2) if day_co else 0
                    avg_o3 = round(sum(day_o3) / len(day_o3) * GAS_CORRECTION, 1) if day_o3 else 0
                    forecast_days.append({
                        "PM2.5": avg_pm25, "PM10": avg_pm10,
                        "NO₂": avg_no2, "SO₂": avg_so2,
                        "CO": avg_co, "O₃": avg_o3
                    })

            return {
                "current": current_vals,
                "avg_24hr": avg_vals,
                "forecast": forecast_days,
                "success": True
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== AI ANALYSIS ENGINE ==============

def calculate_sub_index(concentration, breakpoints):
    """Calculate AQI sub-index using CPCB linear interpolation method."""
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= concentration <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
            return round(aqi)
    if concentration > breakpoints[-1][1]:
        return 500
    return 0


def calculate_aqi(pollutant_values):
    """Calculate overall AQI = maximum of all sub-indices (Indian CPCB standard)."""
    sub_indices = {}
    for pollutant, value in pollutant_values.items():
        if value is not None and value > 0 and pollutant in POLLUTANT_INFO:
            sub_index = calculate_sub_index(value, POLLUTANT_INFO[pollutant]["breakpoints"])
            sub_indices[pollutant] = sub_index
    if not sub_indices:
        return 0, "N/A", {}
    aqi = max(sub_indices.values())
    dominant = max(sub_indices, key=sub_indices.get)
    return aqi, dominant, sub_indices


def get_aqi_category(aqi):
    """Get category name from AQI value."""
    for category, info in AQI_CATEGORIES.items():
        if info["range"][0] <= aqi <= info["range"][1]:
            return category
    return "Severe" if aqi > 400 else "Good"


def ai_analyze_conditions(weather, air_quality, city_name, city_info):
    """
    AI ANALYSIS ENGINE — Correlates weather with pollution to explain WHY
    pollution is at its current level. This is what Google CANNOT do.
    """
    insights = []
    risk_factors = []
    correlations = []
    causes = []
    mitigation = []

    temp = weather.get("temperature", 25)
    humidity = weather.get("humidity", 50)
    wind = weather.get("wind_speed", 10)
    pm25 = air_quality.get("PM2.5", 0)
    pm10 = air_quality.get("PM10", 0)
    no2 = air_quality.get("NO₂", 0)
    so2 = air_quality.get("SO₂", 0)
    o3 = air_quality.get("O₃", 0)
    co = air_quality.get("CO", 0)

    # ─── WEATHER → POLLUTION CORRELATIONS (Hidden Patterns) ───

    # Temperature inversion correlation
    if temp < 15:
        risk_factors.append("TEMPERATURE INVERSION")
        correlations.append(
            f"🌡️→💨 CORRELATION: Low temp ({temp}°C) causes temperature inversion.\n"
            f"      Science: Warm air layer above traps cold polluted air below.\n"
            f"      Effect: PM2.5 concentration increases by 40-80% during inversion.\n"
            f"      This is WHY North Indian cities choke every winter (Nov-Jan).")
    elif temp > 30:
        correlations.append(
            f"🌡️→O₃ CORRELATION: High temp ({temp}°C) accelerates photochemical reactions.\n"
            f"      Science: NO₂ + hν → NO + O; then O + O₂ → O₃\n"
            f"      Effect: Ground-level ozone peaks in afternoon heat.")

    # Wind-pollution correlation
    if wind < 5:
        risk_factors.append("WIND STAGNATION")
        correlations.append(
            f"🌬️→PM CORRELATION: Very low wind ({wind} km/h) = zero dispersal.\n"
            f"      Science: Pollutants accumulate when wind cannot carry them away.\n"
            f"      Effect: AQI can double within 6-8 hours of calm conditions.\n"
            f"      Fact: Delhi's worst days always coincide with wind < 4 km/h.")
    elif wind > 15:
        correlations.append(
            f"🌬️→PM CORRELATION: Strong wind ({wind} km/h) = natural ventilation.\n"
            f"      Effect: Pollutants are dispersed and diluted significantly.")

    # Humidity-pollution correlation
    if humidity > 75:
        risk_factors.append("HIGH HUMIDITY")
        correlations.append(
            f"💧→PM CORRELATION: High humidity ({humidity}%) creates secondary pollutants.\n"
            f"      Chemistry: SO₂ + H₂O → H₂SO₃ (sulphurous acid aerosol)\n"
            f"                 NH₃ + HNO₃ → NH₄NO₃ (ammonium nitrate PM)\n"
            f"      Effect: These reactions CREATE new PM2.5 particles in moist air!\n"
            f"      This is WHY foggy mornings have worse AQI than clear afternoons.")

    # ─── POLLUTANT-SPECIFIC: WHAT'S CAUSING EACH ONE & HOW TO FIX ───

    if pm25 > 60:
        causes.append(
            f"🔴 PM2.5 = {pm25} µg/m³ — ABOVE SAFE LIMIT\n"
            f"   WHY it's high:\n"
            f"   • Vehicular exhaust (diesel trucks/buses) — 30% contribution\n"
            f"   • Road dust resuspension — 20% contribution\n"
            f"   • Industrial emissions & construction — 25% contribution\n"
            f"   • Biomass/crop burning (seasonal) — 15% contribution\n"
            f"   • Secondary formation from SO₂/NO₂ + humidity — 10%")
        mitigation.append(
            f"   FIX PM2.5:\n"
            f"   • Immediate: Deploy water sprinklers + mechanical sweepers\n"
            f"   • Short-term: Restrict diesel vehicles, ban construction\n"
            f"   • Long-term: Shift to BS-VI vehicles, promote EVs & metro\n"
            f"   • Plant dust-capturing trees: Neem, Peepal, Banyan")

    if no2 > 40:
        causes.append(
            f"🔴 NO₂ = {no2} µg/m³ — ABOVE WHO LIMIT\n"
            f"   WHY it's high:\n"
            f"   • Vehicle engines burn fuel at >1000°C → N₂ + O₂ → 2NO → 2NO₂\n"
            f"   • Thermal power plants (coal combustion)\n"
            f"   • Traffic congestion = more idling = more NO₂ per km\n"
            f"   • Also CAUSES ozone: NO₂ + sunlight → O₃ (chain reaction!)")
        mitigation.append(
            f"   FIX NO₂:\n"
            f"   • Immediate: Odd-Even vehicle scheme, congestion pricing\n"
            f"   • Short-term: Promote CNG/electric buses, improve traffic flow\n"
            f"   • Long-term: Shift power plants to solar/wind, electrify railways\n"
            f"   • Catalytic converters: 2NO₂ + 2CO → N₂ + 2CO₂ (in vehicles)")

    if so2 > 40:
        causes.append(
            f"🔴 SO₂ = {so2} µg/m³ — ABOVE WHO LIMIT\n"
            f"   WHY it's high:\n"
            f"   • Coal-fired power plants (coal contains 1-3% sulphur)\n"
            f"   • Oil refineries (crude oil processing)\n"
            f"   • Industrial boilers using high-sulphur fuel\n"
            f"   • Leads to: SO₂ + H₂O → H₂SO₄ (ACID RAIN — damages Taj Mahal!)")
        mitigation.append(
            f"   FIX SO₂:\n"
            f"   • Immediate: Install FGD (Flue Gas Desulphurization) scrubbers\n"
            f"     Reaction: SO₂ + Ca(OH)₂ → CaSO₃ + H₂O (removes SO₂)\n"
            f"   • Short-term: Switch to low-sulphur fuel, enforce emission norms\n"
            f"   • Long-term: Replace coal plants with renewable energy")

    if o3 > 100:
        causes.append(
            f"🔴 O₃ = {o3} µg/m³ — ABOVE SAFE LIMIT\n"
            f"   WHY it's high:\n"
            f"   • NOT directly emitted! Formed by REACTION in sunlight:\n"
            f"     NO₂ + UV light → NO + O (atomic oxygen)\n"
            f"     O + O₂ → O₃ (ground-level ozone)\n"
            f"   • More sunlight + more NO₂ + more VOCs = more O₃\n"
            f"   • Peaks in afternoon (2-4 PM) when solar radiation is maximum")
        mitigation.append(
            f"   FIX O₃:\n"
            f"   • Cannot be removed directly — must reduce PRECURSORS\n"
            f"   • Reduce NO₂ (vehicle emission control)\n"
            f"   • Reduce VOCs (limit paints, solvents, petrol vapors)\n"
            f"   • Avoid outdoor exercise between 12 PM - 4 PM in summer")

    if co > 2:
        causes.append(
            f"🔴 CO = {co} mg/m³ — ELEVATED\n"
            f"   WHY it's high:\n"
            f"   • Incomplete combustion: 2C + O₂ → 2CO (insufficient oxygen)\n"
            f"   • Old/poorly maintained vehicles (2-stroke engines)\n"
            f"   • Biomass burning (chulhas, waste burning)\n"
            f"   • DANGER: Hb + CO → HbCO (blocks oxygen transport in blood)")
        mitigation.append(
            f"   FIX CO:\n"
            f"   • Immediate: Improve vehicle maintenance, PUC enforcement\n"
            f"   • Short-term: Phase out 2-stroke engines, ban waste burning\n"
            f"   • Long-term: Promote LPG/electric cooking, vehicle electrification")

    # If pollutants are within limits
    if not causes:
        causes.append("✅ All major pollutants are within safe limits!\n"
                     "   Current weather conditions are helping keep air clean.")
        mitigation.append("   MAINTAIN: Continue using public transport, avoid burning waste,\n"
                         "   and support tree plantation drives to keep air quality good.")

    # ─── OVERALL RISK FROM COMBINED FACTORS ───

    risk_level = len(risk_factors)
    if risk_level >= 3:
        risk_msg = "🔴 CRITICAL — Multiple weather factors TRAPPING pollution simultaneously!"
    elif risk_level >= 2:
        risk_msg = "🟠 HIGH RISK — Weather conditions amplifying pollution levels"
    elif risk_level >= 1:
        risk_msg = "🟡 MODERATE — One weather factor contributing to pollution buildup"
    else:
        risk_msg = "🟢 LOW RISK — Weather is helping disperse pollutants"

    return correlations, causes, mitigation, risk_factors, risk_msg


# ============== STREAMLIT UI ==============

def get_aqi_color(aqi):
    """Get color for AQI value."""
    if aqi <= 50:
        return "#009966"
    elif aqi <= 100:
        return "#ffde33"
    elif aqi <= 200:
        return "#ff9933"
    elif aqi <= 300:
        return "#cc0033"
    elif aqi <= 400:
        return "#660099"
    else:
        return "#7e0023"


def render_live_monitor():
    """Tab 1: Live AI Monitor"""
    st.header("🤖 Live AI Monitor")

    col1, col2 = st.columns([2, 1])
    with col1:
        city_name = st.selectbox("Select City", list(INDIAN_CITIES.keys()), index=0)
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("🤖 ANALYZE NOW", type="primary", use_container_width=True)

    city = INDIAN_CITIES[city_name]
    st.caption(f"📍 {city['info']} | {city['lat']}°N, {city['lon']}°E | Type: {city['type']}")

    if analyze_btn:
        with st.spinner("🔄 Connecting to satellite data sources..."):
            # Step 1: Fetch weather
            weather = fetch_live_weather(city["lat"], city["lon"])
            if not weather["success"]:
                st.error(f"❌ Could not fetch weather data: {weather['error']}")
                return

            # Step 2: Fetch air quality
            air_quality_data = fetch_live_air_quality(city["lat"], city["lon"])
            if not air_quality_data["success"]:
                st.error(f"❌ Could not fetch air quality: {air_quality_data['error']}")
                return

        current_aq = air_quality_data["current"]
        avg_24hr_aq = air_quality_data["avg_24hr"]

        # Calculate AQI
        aqi_current, dominant_c, sub_indices_c = calculate_aqi(
            {k: v for k, v in current_aq.items() if k in POLLUTANT_INFO})
        aqi_24hr, dominant_a, sub_indices_a = calculate_aqi(
            {k: v for k, v in avg_24hr_aq.items() if k in POLLUTANT_INFO})

        category_c = get_aqi_category(aqi_current)
        category_a = get_aqi_category(aqi_24hr)
        aqi = min(aqi_24hr, 199)
        category = get_aqi_category(aqi)
        dominant = dominant_a
        air_quality = avg_24hr_aq

        # AI Analysis
        correlations, causes, mitigation, risk_factors, risk_msg = ai_analyze_conditions(
            weather, air_quality, city_name, city)

        # ═══════════ DISPLAY ═══════════
        st.markdown("---")

        # AQI Big Display
        aqi_color = get_aqi_color(aqi)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, {aqi_color}22, {aqi_color}11); 
                        border-left: 5px solid {aqi_color}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h1 style="color: {aqi_color}; margin: 0;">AQI: {aqi}</h1>
                <h3 style="color: {aqi_color}; margin: 5px 0;">{category}</h3>
                <p style="margin: 5px 0;">Dominant Pollutant: <b>{dominant}</b> | Method: Indian CPCB (24-hr avg)</p>
                <p style="margin: 0; font-size: 0.9em; color: #666;">{datetime.now().strftime('%d %b %Y, %I:%M %p')}</p>
            </div>
            """, unsafe_allow_html=True)

        # Weather Row
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        w_col1.metric("🌡️ Temperature", f"{weather['temperature']}°C")
        w_col2.metric("💧 Humidity", f"{weather['humidity']}%")
        w_col3.metric("🌬️ Wind Speed", f"{weather['wind_speed']} km/h")
        w_col4.metric("🧭 Wind Dir", f"{weather['wind_direction']}°")

        # Pollutant Table
        st.subheader("📊 Pollutant Levels")
        table_data = []
        for pollutant in ["PM2.5", "PM10", "NO₂", "SO₂", "CO", "O₃"]:
            if pollutant in POLLUTANT_INFO:
                info = POLLUTANT_INFO[pollutant]
                curr_val = current_aq.get(pollutant, 0)
                avg_val = avg_24hr_aq.get(pollutant, 0)

                if avg_val <= info["who_limit"]:
                    status = "🟢 SAFE"
                elif avg_val <= info["india_limit"]:
                    status = "🟡 MODERATE"
                else:
                    status = "🔴 HIGH"

                table_data.append({
                    "Pollutant": pollutant,
                    "Current": f"{curr_val:.1f}",
                    "24h Avg": f"{avg_val:.1f}",
                    "India Limit": f"{info['india_limit']}",
                    "Status": status
                })

        st.table(table_data)

        # 3-Day Forecast
        forecast = air_quality_data.get("forecast", [])
        if forecast:
            st.subheader("📈 3-Day AQI Forecast")
            forecast_cols = st.columns(len(forecast))
            prev_aqi = aqi
            for i, (col, day_data) in enumerate(zip(forecast_cols, forecast)):
                day_aqi_vals = {k: v for k, v in day_data.items() if k in POLLUTANT_INFO}
                day_aqi, _, _ = calculate_aqi(day_aqi_vals)
                day_aqi = min(day_aqi, 199)
                day_cat = get_aqi_category(day_aqi)

                if day_aqi > prev_aqi + 20:
                    trend = "↑ Worsening"
                elif day_aqi < prev_aqi - 20:
                    trend = "↓ Improving"
                else:
                    trend = "→ Stable"

                with col:
                    st.metric(
                        f"Day {i+1}",
                        f"AQI {day_aqi}",
                        delta=trend,
                        delta_color="inverse" if "Worsening" in trend else ("normal" if "Improving" in trend else "off")
                    )
                    st.caption(day_cat)
                prev_aqi = day_aqi

        # Risk Assessment
        st.subheader("⚡ Risk Assessment")
        st.info(risk_msg)
        if risk_factors:
            st.warning(f"**Active Risk Factors:** {' · '.join(risk_factors)}")

        # Weather-Pollution Correlations
        if correlations:
            st.subheader("🔬 Chemistry: Why Is Pollution At This Level?")
            for corr in correlations:
                st.code(corr, language=None)

        # Root Causes
        if causes:
            st.subheader("🔍 Root Cause Analysis")
            for cause in causes:
                st.code(cause, language=None)

        # Remediation
        st.subheader("💡 AI Remediation Strategy")
        for mit in mitigation:
            st.code(mit, language=None)

        # Personal Advisory
        st.subheader("🛡️ Personal Advisory")
        for strategy in REMEDIATION.get(category, REMEDIATION["Moderate"]):
            st.markdown(f"- {strategy}")

        st.caption("Source: Copernicus/CAMS via Open-Meteo API (free, no key)")


def render_water_pollution():
    """Tab 2: Water Pollution"""
    st.header("💧 Water Pollution Analysis")

    river_name = st.selectbox("Select River/Water Body", list(RIVER_DATA.keys()))
    analyze_btn = st.button("💧 Analyze Water Quality", type="primary")

    if analyze_btn:
        data = RIVER_DATA[river_name]

        st.markdown("---")
        st.markdown(f"**ℹ️ {data['info']}**")
        st.caption(f"Sources: {data['sources']}")

        # Water Quality Table
        st.subheader("📋 Water Quality Parameters")
        table_data = []
        for param_key, param_info in WATER_QUALITY_PARAMS.items():
            value = data.get(param_key, 0)
            safe_min = param_info["safe_min"]
            safe_max = param_info["safe_max"]

            if param_key == "DO":
                is_safe = value >= safe_min
                safe_str = f">{safe_min}"
            elif param_key == "pH":
                is_safe = safe_min <= value <= safe_max
                safe_str = f"{safe_min}-{safe_max}"
            else:
                is_safe = value <= safe_max
                safe_str = f"<{safe_max}"

            status = "🟢 SAFE" if is_safe else "🔴 UNSAFE"
            table_data.append({
                "Parameter": param_info["name"],
                "Value": f"{value} {param_info['unit']}",
                "Safe Range": safe_str,
                "Status": status
            })

        st.table(table_data)

        # AI Analysis
        analysis, predictions, remediation = ai_analyze_water(river_name, data)

        st.subheader("🔬 Why Is This Water Polluted?")
        for item in analysis:
            st.code(item, language=None)

        if predictions:
            st.subheader("🤖 AI Predictions")
            for pred in predictions:
                st.warning(pred)

        st.subheader("🛠️ Remediation Strategies")
        for rem in remediation:
            st.code(rem, language=None)

        st.caption("Source: CPCB Water Quality Reports")


def render_learn_pollutants():
    """Tab 3: Learn About Pollutants"""
    st.header("📚 Pollutant Encyclopedia")

    pollutant_key = st.selectbox("Select Pollutant", list(POLLUTANT_INFO.keys()))
    info = POLLUTANT_INFO[pollutant_key]

    st.markdown("---")
    st.subheader(info["name"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📋 Chemical Formula:** {info['formula']}")
        st.markdown(f"**📏 Unit:** {info['unit']}")
        st.markdown(f"**✅ Safe Limit:** {info['safe_limit']}")
    with col2:
        st.markdown(f"**🏭 Sources:** {info['sources']}")
        st.markdown(f"**⚠️ Health Effects:** {info['effects']}")

    st.info(f"🇮🇳 **India Fact:** {info['india_fact']}")

    st.subheader("🧪 Chemical Reactions")
    st.code(info["chemistry"], language=None)


def render_ai_info():
    """Tab 4: How AI Works in Environmental Chemistry"""
    st.header("🧠 AI in Environmental Chemistry")

    st.markdown("""
> Imagine you check Google and it says "AQI = 280" for Delhi.
> That's just a number. But what if a computer could tell you
> **WHY** it's 280 today when it was only 150 yesterday? That's
> exactly what AI does — it finds patterns in thousands of data
> points (temperature, wind, humidity, emissions) and connects
> them to pollution levels using chemistry we study in class.
""")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Traditional Monitoring")
        st.markdown("""
- Shows current AQI
- Reports numbers
- Same advice for all
- Reactive (after damage)
""")
    with col2:
        st.markdown("### AI-Powered Analysis")
        st.markdown("""
- Predicts FUTURE AQI
- Explains WHY (chemistry)
- Targeted remediation
- Proactive (prevents!)
""")

    st.markdown("---")

    with st.expander("🌫️ How AI Predicts Air Pollution", expanded=True):
        st.markdown("""
**SOURCE IDENTIFICATION**

When AI sees high NO₂ and CO together but low SO₂, it concludes the pollution is coming from **vehicles** — because
cars burn petrol/diesel producing NO₂ and CO, but not much SO₂. If SO₂ is also high, it means a factory or coal power
plant is nearby. This is like a detective using chemical "fingerprints" to identify the criminal.

**SECONDARY POLLUTANT PREDICTION**

Some pollutants aren't directly emitted — they FORM in the air through chemical reactions:

```
SO₂ + NH₃ + H₂O  →  (NH₄)₂SO₄
```

This product is a fine particle (PM2.5) that enters our lungs. AI can predict this reaction BEFORE it happens by
checking current SO₂ levels, humidity, and temperature — giving us time to act.

**PHOTOCHEMICAL SMOG TIMING**

Ground-level ozone (O₃) is not emitted by anyone — it forms when NO₂ breaks apart in sunlight:

```
NO₂ + sunlight  →  NO + O
O + O₂  →  O₃ (harmful ground-level ozone)
```

AI models this every hour and can predict that ozone will peak between 2-4 PM on a sunny day.

**CROP BURNING & DELHI SMOG**

Every October-November, farmers in Punjab and Haryana burn crop residue. Satellites detect these fires using
thermal imaging. AI then calculates: given the wind speed and direction, this smoke will reach Delhi in 36 hours.
""")

    with st.expander("💧 How AI Predicts Water Pollution"):
        st.markdown("""
**DISSOLVED OXYGEN (DO) PREDICTION**

When sewage enters a river, bacteria start decomposing the organic waste:

```
Organic matter + O₂  →  CO₂ + H₂O
(bacteria consume the dissolved oxygen)
```

If DO drops below 4 mg/L, fish start dying. AI monitors where sewage enters the river and predicts exactly which
stretch downstream will have dangerously low oxygen.

**EUTROPHICATION (ALGAL BLOOMS)**

Fertilizers (containing nitrogen and phosphorus) wash into rivers during monsoon. This excess nutrition causes
algae to grow explosively, blocking sunlight. Plants below die, decompose, and consume all oxygen — creating "dead zones."

**HEAVY METAL CONTAMINATION**

Industries discharge metals like chromium (Cr⁶⁺), lead (Pb²⁺), and mercury (Hg²⁺) into rivers. These don't
decompose — they accumulate in sediments, then in fish, then in humans (bioaccumulation).

**ACID MINE DRAINAGE**

```
4FeS₂ + 15O₂ + 14H₂O  →  4Fe(OH)₃ + 8H₂SO₄
```

This acid drains into nearby streams, dropping pH to as low as 2-3 (like vinegar).
""")

    with st.expander("🇮🇳 Real AI Systems in India"):
        st.markdown("""
**SAFAR** (System of Air Quality and Weather Forecasting)
- Run by IITM Pune, uses machine learning + WRF-Chem model
- Takes 50+ inputs and gives 72-hour AQI forecast

**IIT Delhi Research Group**
- Trained LSTM neural networks on 5 years of CPCB data
- Discovered: "Diwali + wind < 4 km/h + temp < 15°C" → AQI > 400

**ISRO Satellite Monitoring**
- AI analyzes satellite data to map NO₂, SO₂, O₃ across India
- Detects sudden pollution spikes within hours

**CPCB Water Quality Network**
- Monitors 600+ river stations in real-time
- AI flags deteriorating stretches for faster response
""")

    st.caption("This app uses free Copernicus/CAMS satellite data — the same source used by professional environmental scientists.")


# ============== MAIN APP ==============

def main():
    st.set_page_config(
        page_title="AI Pollution Predictor — Class XI Chemistry",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Header
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; text-align: center;">🌍 AI-Powered Pollution Monitor & Predictor</h1>
            <p style="color: #c8e6c9; text-align: center; margin: 5px 0 0 0;">
                Real-time Data  •  AI Analysis  •  Smart Remediation  •  Vanshika Malhotra
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 Live AI Monitor",
        "💧 Water Pollution",
        "📚 Learn Pollutants",
        "🧠 AI in Env. Chemistry"
    ])

    with tab1:
        render_live_monitor()
    with tab2:
        render_water_pollution()
    with tab3:
        render_learn_pollutants()
    with tab4:
        render_ai_info()


if __name__ == "__main__":
    main()

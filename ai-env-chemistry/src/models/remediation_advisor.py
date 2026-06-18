"""
Remediation strategy recommender.
Maps predicted pollution levels to evidence-based remediation actions
using a rule-based system combined with an ML classifier.
"""
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


# -------------------------------------------------------------------------
# Remediation knowledge base
# -------------------------------------------------------------------------
REMEDIATION_STRATEGIES = {
    # Air pollution
    "air_high_PM": [
        "Install industrial particulate filters (HEPA / electrostatic precipitators)",
        "Enforce emission reduction protocols at identified point sources",
        "Increase urban green buffer zones and tree canopy",
        "Issue public health advisories and restrict outdoor activity",
    ],
    "air_high_NO2": [
        "Introduce catalytic converter requirements for vehicles",
        "Promote electrification of transport fleet",
        "Apply selective catalytic reduction (SCR) at industrial stacks",
    ],
    "air_high_O3": [
        "Reduce VOC and NOx precursor emissions",
        "Adjust industrial operations to off-peak hours",
        "Monitor photochemical smog formation indices",
    ],
    # Water contamination
    "water_high_lead": [
        "Replace lead service pipes and plumbing infrastructure",
        "Apply corrosion inhibitors (orthophosphate dosing) in distribution systems",
        "Install point-of-use filtration (reverse osmosis)",
        "Issue do-not-drink advisories for affected zones",
    ],
    "water_high_arsenic": [
        "Deploy coagulation-flocculation treatment with iron salts",
        "Use adsorption media (activated alumina, iron oxide coated sand)",
        "Explore alternative groundwater sources or rainwater harvesting",
        "Monitor smelter and mining discharge in upstream catchments",
    ],
    "water_high_nitrates": [
        "Implement buffer strips along agricultural fields",
        "Introduce constructed wetlands for nutrient removal",
        "Regulate fertilizer application timing and rates",
        "Upgrade wastewater treatment to biological nitrogen removal",
    ],
    # Soil contamination
    "soil_heavy_metals": [
        "Phytoremediation: deploy hyperaccumulator plants (e.g., Thlaspi caerulescens for Zn/Cd)",
        "Soil washing with chelating agents (EDTA) for mobile metals",
        "Immobilization using lime, zeolites, or phosphate amendments",
        "Excavation and landfill disposal for highly contaminated hotspots",
    ],
    "soil_organics": [
        "Bioremediation: stimulate indigenous microbial degradation (biostimulation)",
        "Bioaugmentation with specialized hydrocarbon-degrading bacteria",
        "Chemical oxidation with persulfate or Fenton's reagent",
        "Thermal treatment (soil vapor extraction, thermal desorption)",
    ],
}


class RemediationAdvisor:
    """
    Classifies contamination type and returns prioritized remediation actions.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.classifier = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=4,
            random_state=random_state,
        )
        self.is_trained = False
        self.classes_ = None

    def train(self, X, y, test_size: float = 0.2):
        """Fit classifier on labeled contamination scenarios."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        self.classifier.fit(X_train, y_train)
        self.is_trained = True
        self.classes_ = list(self.classifier.classes_)

        y_pred = self.classifier.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        return report

    def predict_strategy_key(self, X) -> list:
        """Return predicted contamination type keys for each sample."""
        if not self.is_trained:
            raise RuntimeError("Advisor must be trained first.")
        return self.classifier.predict(X).tolist()

    def recommend(self, strategy_key: str) -> list:
        """Return list of remediation actions for a given strategy key."""
        if strategy_key not in REMEDIATION_STRATEGIES:
            return [f"No strategy found for key '{strategy_key}'. Review pollution data."]
        return REMEDIATION_STRATEGIES[strategy_key]

    def rule_based_recommend(self, pollution_row: dict) -> dict:
        """
        Fast rule-based recommendation without ML.
        pollution_row: dict of measured values, e.g.:
            {"PM2_5": 120, "NO2": 80, "lead_ugl": 15, "nitrates_mgl": 25}
        Returns dict of {issue: [strategies]}.
        """
        recommendations = {}

        if pollution_row.get("PM2_5", 0) > 75:
            recommendations["air_high_PM"] = REMEDIATION_STRATEGIES["air_high_PM"]
        if pollution_row.get("NO2", 0) > 100:
            recommendations["air_high_NO2"] = REMEDIATION_STRATEGIES["air_high_NO2"]
        if pollution_row.get("O3", 0) > 120:
            recommendations["air_high_O3"] = REMEDIATION_STRATEGIES["air_high_O3"]
        if pollution_row.get("lead_ugl", 0) > 10:
            recommendations["water_high_lead"] = REMEDIATION_STRATEGIES["water_high_lead"]
        if pollution_row.get("arsenic_ugl", 0) > 5:
            recommendations["water_high_arsenic"] = REMEDIATION_STRATEGIES["water_high_arsenic"]
        if pollution_row.get("nitrates_mgl", 0) > 50:
            recommendations["water_high_nitrates"] = REMEDIATION_STRATEGIES["water_high_nitrates"]

        if not recommendations:
            recommendations["status"] = ["All measured values within acceptable thresholds."]

        return recommendations

    def save(self, path: str):
        joblib.dump(self.classifier, path)

    def load(self, path: str):
        self.classifier = joblib.load(path)
        self.is_trained = True
        self.classes_ = list(self.classifier.classes_)

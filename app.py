import joblib
import json
from pathlib import Path
import joblib
from pathlib import Path
from flask import Flask, request, jsonify

import pandas as pd
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # ← add this line right after creating app

# -----------------------------------------------------------------------------
# Flask App
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Load Artifacts
# -----------------------------------------------------------------------------

ARTIFACT_DIR = Path("artifacts")

model = joblib.load(ARTIFACT_DIR / "model.joblib")
encoders = joblib.load(ARTIFACT_DIR / "encoders.joblib")

with open(ARTIFACT_DIR / "metadata.json", "r") as f:
    metadata = json.load(f)

route_stats = pd.read_csv(ARTIFACT_DIR / "route_stats.csv")
agency_stats = pd.read_csv(ARTIFACT_DIR / "agency_stats.csv")

print("✅ All artifacts loaded successfully")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def safe_encode(column, value):
    """
    Safely encode categorical values.
    Unknown values return 0.
    """

    le = encoders[column]

    if value in le.classes_:
        return int(le.transform([value])[0])

    return 0


def get_route_features(from_city, to_city):

    route_key = f"{from_city} → {to_city}"

    match = route_stats[
        route_stats["route"] == route_key
    ]

    if len(match) > 0:

        row = match.iloc[0]

        return {
            "route_mean_price": row["route_mean_price"],
            "route_median_price": row["route_median_price"],
            "route_min_price": row["route_min_price"],
            "route_max_price": row["route_max_price"],
            "route_count": row["route_count"],
            "route_price_range": row["route_price_range"]
        }

    return metadata["global_route"]


def get_agency_mean_price(agency):

    match = agency_stats[
        agency_stats["agency"] == agency
    ]

    if len(match) > 0:
        return float(match.iloc[0]["agency_mean_price"])

    return metadata["global_agency"]["agency_mean_price"]


# -----------------------------------------------------------------------------
# Prediction Function
# -----------------------------------------------------------------------------

def predict_price(record):

    required_fields = [
        "from_city",
        "to_city",
        "flight_type",
        "agency",
        "date"
    ]

    for field in required_fields:
        if field not in record:
            raise ValueError(f"Missing required field: {field}")

    from_city = record["from_city"]
    to_city = record["to_city"]
    flight_type = record["flight_type"]
    agency = record["agency"]

    age = int(record.get("age", 35))
    gender = record.get("gender", "none")

    # -------------------------------------------------------------------------
    # Validate flight type
    # -------------------------------------------------------------------------

    if flight_type not in metadata["class_map"]:
        raise ValueError(
            f"Invalid flight_type. Must be one of: "
            f"{list(metadata['class_map'].keys())}"
        )

    # -------------------------------------------------------------------------
    # Date Features
    # -------------------------------------------------------------------------

    dt = pd.to_datetime(record["date"])

    month = dt.month
    day_of_week = dt.dayofweek
    is_weekend = int(day_of_week in [5, 6])
    quarter = dt.quarter

    # -------------------------------------------------------------------------
    # Encodings
    # -------------------------------------------------------------------------

    flightClass_ord = metadata["class_map"][flight_type]

    from_enc = safe_encode("from", from_city)
    to_enc = safe_encode("to", to_city)

    agency_enc = safe_encode(
        "agency",
        agency
    )

    gender_enc = safe_encode(
        "gender",
        gender
    )

    # -------------------------------------------------------------------------
    # Route Statistics
    # -------------------------------------------------------------------------

    route_features = get_route_features(
        from_city,
        to_city
    )

    # -------------------------------------------------------------------------
    # Agency Statistics
    # -------------------------------------------------------------------------

    agency_mean_price = get_agency_mean_price(
        agency
    )

    # -------------------------------------------------------------------------
    # Build Feature Vector
    # -------------------------------------------------------------------------

    X = pd.DataFrame([{
        "flightClass_ord": flightClass_ord,
        "from_enc": from_enc,
        "to_enc": to_enc,
        "agency_enc": agency_enc,
        "age": age,
        "gender_enc": gender_enc,
        "month": month,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "quarter": quarter,
        "route_mean_price": route_features["route_mean_price"],
        "route_median_price": route_features["route_median_price"],
        "route_min_price": route_features["route_min_price"],
        "route_max_price": route_features["route_max_price"],
        "route_count": route_features["route_count"],
        "route_price_range": route_features["route_price_range"],
        "agency_mean_price": agency_mean_price
    }])

    # Ensure exact feature order

    X = X[metadata["features"]]

    prediction = float(
        model.predict(X)[0]
    )

    return {
        "predicted_price": round(prediction, 2),
        "currency": "BRL",
        "route": f"{from_city} → {to_city}",
        "flight_type": flight_type,
        "model": metadata["model_name"],
        "test_r2": metadata["test_metrics"]["R2"]
    }


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Flight Price Prediction API Running",
        "model": metadata["model_name"],
        "r2": metadata["test_metrics"]["R2"],
        "feature_count": len(metadata["features"])
    })


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "model": metadata["model_name"]
    })


@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        if data is None:
            return jsonify({
                "error": "No JSON body received"
            }), 400

        result = predict_price(data)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
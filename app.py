from flask import Flask, request, jsonify
import math
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
disease_coeffs = {
    "cardiovascular": {
        "name": "Сердечно-сосудистые заболевания",
        "base": -3.0,
        "age": 0.05,
        "sex_male": 0.6,
        "bmi": 0.08,
        "systolic": 0.02,
        "smoking": 1.0,
        "diabetes": 1.5,
        "cholesterol": 0.3,
        "physical_activity": -0.4
    },
    "lung_cancer": {
        "name": "Рак лёгких",
        "base": -5.5,
        "age": 0.15,
        "sex_male": 0.5,
        "bmi": -0.01,
        "systolic": 0.0,
        "smoking": 4.0,
        "diabetes": 0.0,
        "cholesterol": 0.0,
        "physical_activity": -0.3
    },
    "hypertension": {
        "name": "Артериальная гипертензия",
        "base": -3.5,
        "age": 0.05,
        "sex_male": 0.4,
        "bmi": 0.10,
        "systolic": 0.05,
        "smoking": 0.6,
        "diabetes": 0.8,
        "cholesterol": 0.1,
        "physical_activity": -0.2
    },
    "obesity": {
        "name": "Ожирение",
        "base": -3.2,
        "age": 0.02,
        "sex_male": -0.2,
        "bmi": 0.45,
        "systolic": 0.01,
        "smoking": -0.1,
        "diabetes": 1.2,
        "cholesterol": 0.05,
        "physical_activity": -0.9
    },
    "ckd": {
        "name": "Хроническая болезнь почек (ХБП)",
        "base": -5.0,
        "age": 0.10,
        "sex_male": 0.2,
        "bmi": 0.05,
        "systolic": 0.03,
        "smoking": 0.5,
        "diabetes": 1.5,
        "cholesterol": 0.1,
        "physical_activity": -0.3
    }
}

defs = {
    "age": 50.0,
    "bmi": 25.0,
    "systolic": 120.0,
    "cholesterol": 5.0,
    "physical_activity": 1
}


def calc_score(data, coeffs):
    score = coeffs["base"]
    score += coeffs["age"] * (data["age"] - defs["age"])
    score += coeffs["sex_male"] * data["sex"]
    score += coeffs["bmi"] * (data["bmi"] - defs["bmi"])
    score += coeffs["systolic"] * (data["systolic"] - defs["systolic"])
    score += coeffs["smoking"] * data["smoking"]
    score += coeffs["diabetes"] * data["diabetes"]
    score += coeffs["cholesterol"] * (data["cholesterol"] - defs["cholesterol"])
    score += coeffs["physical_activity"] * (
        data["physical_activity"] - defs["physical_activity"]
    )
    return score


def score_to_probability(score):
    return 1.0 / (1.0 + math.exp(-score))


def category_from_prob(p):
    if p < 0.05:
        return "очень низкий"
    if p < 0.10:
        return "низкий"
    if p < 0.20:
        return "средний"
    if p < 0.30:
        return "высокий"
    return "очень высокий"


@app.route("/predict", methods=["POST"])
def predict():
    try:
        body = request.json

        disease = body.get("disease")

        if disease not in disease_coeffs:
            return jsonify({
                "error": "Unknown disease",
                "available_diseases": list(disease_coeffs.keys())
            }), 400

        data = {
            "age": float(body["age"]),
            "sex": int(body["sex"]),  
            "bmi": float(body["bmi"]),
            "systolic": float(body["systolic"]),
            "smoking": int(body["smoking"]),
            "diabetes": int(body["diabetes"]),
            "cholesterol": float(body["cholesterol"]),
            "physical_activity": int(body["physical_activity"])
        }

        coeffs = disease_coeffs[disease]

        score = calc_score(data, coeffs)
        probability = score_to_probability(score)
        category = category_from_prob(probability)

        return jsonify({
            "disease": coeffs["name"],
            "score": round(score, 4),
            "probability": round(probability, 4),
            "probability_percent": round(probability * 100, 2),
            "risk_category": category
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "endpoint": "/predict"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
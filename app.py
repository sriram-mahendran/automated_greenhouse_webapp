from flask import Flask, render_template, request, jsonify
import os
import cv2
import requests
import datetime
import joblib
import numpy as np
from datetime import datetime, timedelta

from models.growth_model_1 import (
    HybridGrowthSystem,
    visualize_vegetation,
    visualize_yolo
)

from models.deficiency_model import predict_deficiency
from models.disease_model import detect_disease

runtime_model = joblib.load("weights/pump_runtime_model.pkl")
time_model = joblib.load("weights/next_irrigation_model.pkl")
scaler = joblib.load("weights/irrigation_scaler.pkl")


app = Flask(__name__)


# ---------------- FOLDERS ----------------

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# ---------------- LOAD MODELS ----------------

growth_system = HybridGrowthSystem(
    yolo_path="weights/best.pt"
)


# ---------------- PAGE ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sensors")
def sensors():
    return render_template("sensors.html")


@app.route("/growth")
def growth():
    return render_template("growth.html")


@app.route("/disease")
def disease():
    return render_template("disease.html")


@app.route("/deficiency")
def deficiency():
    return render_template("deficiency.html")


@app.route("/irrigation")
def irrigation():
    return render_template("irrigation.html")

# ---------------- GROWTH API ----------------
@app.route("/api/growth", methods=["POST"])
def api_growth():

    file = request.files["image"]

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(upload_path)

    img = cv2.imread(upload_path)

    result = growth_system.predict(img)

    result_img_path = os.path.join(RESULT_FOLDER,"growth_result.jpg")
    mask_path = os.path.join(RESULT_FOLDER,"leaf_mask.jpg")
    skeleton_path = os.path.join(RESULT_FOLDER,"skeleton.jpg")


    if result["mode"] == "vegetative":

        cv2.imwrite(mask_path, result["mask"])
        cv2.imwrite(skeleton_path, result["skeleton"]*255)

        output_img = visualize_vegetation(
            img,
            result["mask"],
            result["skeleton"],
            result["endpoints"],
            result["growth"]
        )

        cv2.imwrite(result_img_path, output_img)

        return jsonify({
            "mode":result["mode"],
            "growth":float(result["growth"]),
            "mask_image":"/"+mask_path,
            "skeleton_image":"/"+skeleton_path,
            "result_image":"/"+result_img_path
        })


    else:

        output_img = visualize_yolo(
            img,
            result["detections"],
            result["growth"]
        )

        cv2.imwrite(result_img_path, output_img)

        return jsonify({
            "mode":result["mode"],
            "growth":float(result["growth"]),
            "result_image":"/"+result_img_path
        })

# ---------------- DEFICIENCY API ----------------

@app.route("/api/deficiency", methods=["POST"])
def api_deficiency():

    file = request.files["image"]

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(upload_path)

    prediction = predict_deficiency(upload_path)

    return jsonify({

        "prediction": prediction,
        "image": "/" + upload_path

    })


# ---------------- DISEASE API ----------------

@app.route("/api/disease", methods=["POST"])
def api_disease():

    file = request.files["image"]

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(upload_path)

    output_path, diseases = detect_disease(upload_path)

    return jsonify({

        "image": "/" + output_path,
        "diseases": diseases

    })

@app.route("/api/growth_comparison")
def growth_comparison():

    greenhouse_folder = "static/plant_monitor/greenhouse"
    outdoor_folder = "static/plant_monitor/outdoor"

    greenhouse_growth = []
    outdoor_growth = []

    # greenhouse images
    for img_name in os.listdir(greenhouse_folder):

        path = os.path.join(greenhouse_folder, img_name)

        img = cv2.imread(path)

        result = growth_system.predict(img)

        greenhouse_growth.append(result["growth"])


    # outdoor images
    for img_name in os.listdir(outdoor_folder):

        path = os.path.join(outdoor_folder, img_name)

        img = cv2.imread(path)

        result = growth_system.predict(img)

        outdoor_growth.append(result["growth"])


    avg_greenhouse = sum(greenhouse_growth) / len(greenhouse_growth)
    avg_outdoor = sum(outdoor_growth) / len(outdoor_growth)

    improvement = avg_greenhouse - avg_outdoor


    return jsonify({

        "greenhouse_avg": avg_greenhouse,
        "outdoor_avg": avg_outdoor,
        "improvement": improvement

    })
@app.route("/api/irrigation")
def irrigation_data():

    READ_KEY = "27IWGDKREB0YKRUA"
    CHANNEL_ID = "3301033"

    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_KEY}&results=200"

    try:

        r = requests.get(url, timeout=5)
        data = r.json()

    except:
        return jsonify({"error": "Failed to fetch ThingSpeak data"})


    feeds = data.get("feeds", [])

    if len(feeds) == 0:
        return jsonify({"error": "No data available"})


    latest = feeds[-1]

    # -------------------------
    # SENSOR VALUES
    # -------------------------

    soil = float(latest.get("field1") or 0)
    temp = float(latest.get("field2") or 0)
    hum = float(latest.get("field3") or 0)

    actual_runtime = float(latest.get("field4") or 0)
    fan_state = int(float(latest.get("field5") or 0))

    dry_rate = float(latest.get("field6") or 0)

    # -------------------------
    # ML PREDICTIONS
    # -------------------------

    predicted_runtime = float(latest.get("field7") or 0)
    predicted_next = float(latest.get("field8") or 0)

    flow_rate = 3.75

    next_volume = predicted_runtime * flow_rate

    # -------------------------
    # FIND LAST IRRIGATION
    # -------------------------

    last_irrigation = None
    prev_runtime = 0

    for feed in reversed(feeds):

        runtime = feed.get("field4")

        if runtime and float(runtime) > 0:

            last_irrigation = feed.get("created_at")
            prev_runtime = float(runtime)
            break

    prev_volume = prev_runtime * flow_rate


    # -------------------------
    # RESPONSE
    # -------------------------

    return jsonify({

        "soil": soil,
        "temperature": temp,
        "humidity": hum,

        "dry_rate": dry_rate,

        "fan_state": fan_state,
        "actual_runtime": actual_runtime,

        "flow_rate": flow_rate,

        "last_irrigation": last_irrigation,

        "prev_runtime": prev_runtime,
        "prev_volume": prev_volume,

        "next_runtime": predicted_runtime,
        "next_irrigation_minutes": predicted_next,
        "next_volume": next_volume
    })


# ================================
# THINGSPEAK RAW DATA API
# ================================

@app.route("/api/thingspeak")
def thingspeak():

    READ_KEY = "27IWGDKREB0YKRUA"
    CHANNEL_ID = "3301033"

    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_KEY}&results=10"

    try:

        response = requests.get(url, timeout=5)
        return jsonify(response.json())

    except:
        return jsonify({"error": "Failed to fetch ThingSpeak data"})

# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)
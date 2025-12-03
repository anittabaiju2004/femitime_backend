import os
import pickle
import re
import fitz     # PyMuPDF
import pandas as pd
from django.conf import settings

# Full path to ml_assets
ML_PATH = os.path.join(settings.BASE_DIR, "femitimeapp", "ml_assets")

# Load model assets
model = pickle.load(open(os.path.join(ML_PATH, "best_model.pkl"), "rb"))
scaler = pickle.load(open(os.path.join(ML_PATH, "scaler.pkl"), "rb"))
label_encoder = pickle.load(open(os.path.join(ML_PATH, "label_encoder.pkl"), "rb"))

# -----------------------------
# Blood Group Encoder
# -----------------------------
def encode_blood_group(bg: str):
    mapping = {
        "A+": 0, "A-": 1,
        "B+": 2, "B-": 3,
        "AB+": 4, "AB-": 5,
        "O+": 6, "O-": 7
    }
    return mapping.get(bg.upper().strip(), 0)


# -----------------------------
# Maps strings → 0–3 values
# -----------------------------
def map_fast_food(value: str):
    mapping = {
        "never": 0,
        "rarely": 1,
        "often": 2,
        "daily": 3
    }
    return mapping.get(value.lower().strip(), 0)


def map_cycle(value: str):
    mapping = {
        "regular": 0,
        "irregular": 1
    }
    return mapping.get(value.lower().strip(), 0)


def map_severity(value: str):
    mapping = {
        "none": 0,
        "mild": 1,
        "moderate": 2,
        "severe": 3
    }
    return mapping.get(value.lower().strip(), 0)


# -----------------------------
# Extract medical test values from PDF
# -----------------------------
def extract_medical_values(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    fields = {
        "TSH": None,
        "VitaminD": None,
        "Glucose": None,
        "LH": None,
        "FSH": None,
        "Prolactin": None,
        "Testosterone": None,
        "Hemoglobin": None
    }

    for key in fields:
        match = re.search(rf"{key}\s*[:\-]?\s*([0-9.]+)", text, re.IGNORECASE)
        if match:
            fields[key] = float(match.group(1))

    return fields


# -----------------------------
# Convert everything into ML-ready row
# -----------------------------
def prepare_final_df(user_input, pdf_values):
    cols = [
        "Age", "Weight", "Height", "BMI",
        "Fast_Food_Consumption", "Blood_Group", "Pulse_Rate",
        "Cycle_Regularity", "Hair_Growth", "Acne",
        "Mood_Swings", "Skin_Darkening",
        "TSH", "VitaminD", "Glucose", "LH", "FSH",
        "Prolactin", "Testosterone", "Hemoglobin"
    ]

    result = {}
    for col in cols:
        if col in user_input:
            result[col] = user_input[col]
        elif col in pdf_values:
            result[col] = pdf_values[col]
        else:
            result[col] = 0

    return pd.DataFrame([result])
# ETAwise AI Prediction Engine

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "model"
    / "etawise_model.joblib"
)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def predict_delivery_time(
    distance,
    traffic,
    weather,
    vehicle_condition
):
    model = load_model()

    # Convert website selections into training categories
    traffic_mapping = {
        "Low": "Low",
        "Medium": "Medium",
        "High": "High",
        "Jam": "Jam"
    }

    weather_mapping = {
        "Sunny": "conditions Sunny",
        "Cloudy": "conditions Cloudy",
        "Windy": "conditions Windy",
        "Fog": "conditions Fog",
        "Sandstorms": "conditions Sandstorms",
        "Stormy": "conditions Stormy"
    }

    vehicle_mapping = {
        "Poor": 0,
        "Average": 1,
        "Good": 2
    }

    # Create one delivery record
    delivery = pd.DataFrame([{
        "Delivery_person_Age": 30,
        "Delivery_person_Ratings": 4.5,
        "Vehicle_condition": vehicle_mapping[vehicle_condition],
        "multiple_deliveries": 0,
        "Distance_km": distance,
        "Order_DayOfWeek": 2,
        "Order_Month": 3,
        "Is_Weekend": 0,
        "Order_Hour": 14,
        "Preparation_Time_Min": 15,
        "Weatherconditions": weather_mapping[weather],
        "Road_traffic_density": traffic_mapping[traffic],
        "Type_of_order": "Meal",
        "Type_of_vehicle": "motorcycle",
        "Festival": "No",
        "City": "Urban"
    }])

    prediction = model.predict(delivery)[0]

    return round(float(prediction), 1)
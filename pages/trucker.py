import streamlit as st
import pandas as pd

from utils.predictor import predict_delivery_time


def show_trucker_page():

    st.title("🚚 Trucker Dashboard")
    st.markdown("### Your Deliveries, Your Decisions.")
    st.write(
        "Monitor assigned deliveries, review delivery conditions, "
        "and generate AI-powered delivery estimates."
    )

    st.caption("Demonstration dashboard — delivery assignments are simulated.")

    st.divider()

    # Sample delivery assignments
    deliveries = pd.DataFrame([
        {
            "Package ID": "ETA-1001",
            "Destination": "Downtown",
            "Distance (km)": 8.5,
            "Status": "In Transit"
        },
        {
            "Package ID": "ETA-1002",
            "Destination": "North District",
            "Distance (km)": 15.0,
            "Status": "Pending"
        },
        {
            "Package ID": "ETA-1003",
            "Destination": "West District",
            "Distance (km)": 12.0,
            "Status": "Pending"
        },
        {
            "Package ID": "ETA-1004",
            "Destination": "South District",
            "Distance (km)": 6.5,
            "Status": "Delivered"
        }
    ])

    # Dashboard metrics
    total = len(deliveries)
    completed = (deliveries["Status"] == "Delivered").sum()
    remaining = total - completed

    col1, col2, col3 = st.columns(3)

    col1.metric("📦 Assigned Deliveries", total)
    col2.metric("✅ Completed", completed)
    col3.metric("🚚 Remaining", remaining)

    st.divider()

    # Delivery table
    st.subheader("📋 Assigned Deliveries")

    status_filter = st.multiselect(
        "Filter by Delivery Status",
        options=deliveries["Status"].unique().tolist(),
        default=deliveries["Status"].unique().tolist()
    )

    filtered = deliveries[
        deliveries["Status"].isin(status_filter)
    ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # AI estimator
    st.subheader("🧠 AI Delivery Estimator")

    active_deliveries = deliveries[
        deliveries["Status"] != "Delivered"
    ]

    with st.form("trucker_estimator"):

        selected_id = st.selectbox(
            "Select a Delivery",
            active_deliveries["Package ID"].tolist()
        )

        selected_delivery = active_deliveries[
            active_deliveries["Package ID"] == selected_id
        ].iloc[0]

        distance = st.number_input(
            "Delivery Distance (km)",
            min_value=0.1,
            max_value=100.0,
            value=float(selected_delivery["Distance (km)"]),
            step=0.5
        )

        traffic = st.select_slider(
            "Traffic Density",
            options=["Low", "Medium", "High", "Jam"],
            value="Medium"
        )

        weather = st.select_slider(
            "Weather Conditions",
            options=[
                "Sunny", "Cloudy", "Windy",
                "Fog", "Sandstorms", "Stormy"
            ],
            value="Sunny"
        )

        vehicle_condition = st.select_slider(
            "Vehicle Condition",
            options=["Poor", "Average", "Good"],
            value="Average"
        )

        submitted = st.form_submit_button(
            "🚀 Estimate Delivery Time",
            use_container_width=True
        )

    if submitted:

        prediction = predict_delivery_time(
            distance=distance,
            traffic=traffic,
            weather=weather,
            vehicle_condition=vehicle_condition
        )

        st.session_state.trucker_prediction = {
            "package": selected_id,
            "distance": distance,
            "traffic": traffic,
            "weather": weather,
            "prediction": prediction
        }

    if "trucker_prediction" in st.session_state:

        result = st.session_state.trucker_prediction

        st.success(
            f"Prediction generated for {result['package']}!"
        )

        st.metric(
            "Estimated Delivery Duration",
            f"{result['prediction']:.1f} minutes"
        )

        st.caption(
            "Prototype prediction based on a food-delivery dataset. "
            "This is an estimated total duration, not live remaining travel time."
        )
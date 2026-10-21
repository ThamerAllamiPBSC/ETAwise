import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path


# ---------------------------------------------------
# FILE PATHS
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"


# ---------------------------------------------------
# LOAD MODEL EVALUATION DATA
# ---------------------------------------------------

@st.cache_data
def load_model_data():

    files = {
        "predictions": MODEL_DIR / "test_predictions.csv",
        "comparison": MODEL_DIR / "model_comparison.csv",
        "importance": MODEL_DIR / "feature_importance.csv"
    }

    data = {}

    for name, path in files.items():

        if path.exists():
            data[name] = pd.read_csv(path)
        else:
            data[name] = pd.DataFrame()

    return data


# ---------------------------------------------------
# SIMULATED DELIVERY DATA
# ---------------------------------------------------

@st.cache_data
def generate_delivery_data():

    rng = np.random.default_rng(42)

    drivers = [
        "Driver A",
        "Driver B",
        "Driver C",
        "Driver D",
        "Driver E",
        "Driver F"
    ]

    locations = [
        "Downtown",
        "North District",
        "South District",
        "East District",
        "West District",
        "Industrial Zone"
    ]

    traffic_levels = ["Low", "Medium", "High", "Jam"]

    statuses = [
        "Delivered",
        "In Transit",
        "Pending",
        "Delayed"
    ]

    records = []

    for i in range(1, 101):

        distance = round(float(rng.uniform(2, 35)), 1)

        traffic = rng.choice(
            traffic_levels,
            p=[0.25, 0.40, 0.25, 0.10]
        )

        status = rng.choice(
            statuses,
            p=[0.50, 0.30, 0.10, 0.10]
        )

        estimated_time = round(
            12 + distance * 0.7
            + (8 if traffic == "Jam" else 0)
            + float(rng.normal(0, 3)),
            1
        )

        estimated_time = max(5, estimated_time)

        actual_time = round(
            estimated_time + float(rng.normal(2, 5)),
            1
        )

        records.append({
            "Delivery ID": f"ETW-{i:04d}",
            "Driver": str(rng.choice(drivers)),
            "Destination": str(rng.choice(locations)),
            "Distance (km)": distance,
            "Traffic": str(traffic),
            "Status": str(status),
            "Estimated Time (min)": estimated_time,
            "Actual Time (min)": (
                max(1, actual_time)
                if status == "Delivered"
                else np.nan
            )
        })

    return pd.DataFrame(records)


# ---------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------

def show_admin_page():

    st.title("🖥️ Administrator Dashboard")

    st.markdown("### ETAwise Logistics Control Center")

    st.write(
        "Monitor delivery operations, analyze performance, "
        "and evaluate the ETAwise prediction model."
    )

    st.info(
        "📌 Operational deliveries on this page are simulated "
        "for demonstration purposes. AI model evaluation "
        "results are loaded from the project's test data."
    )

    st.divider()

    # Load data
    deliveries = generate_delivery_data()
    model_data = load_model_data()

    # ---------------------------------------------------
    # SECTION 1: OPERATIONS OVERVIEW
    # ---------------------------------------------------

    st.header("📊 Operations Overview")

    total_deliveries = len(deliveries)

    completed = (
        deliveries["Status"] == "Delivered"
    ).sum()

    in_transit = (
        deliveries["Status"] == "In Transit"
    ).sum()

    delayed = (
        deliveries["Status"] == "Delayed"
    ).sum()

    avg_eta = deliveries[
        "Estimated Time (min)"
    ].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Total Deliveries",
            f"{total_deliveries}"
        )

    with col2:
        st.metric(
            "✅ Completed",
            f"{completed}"
        )

    with col3:
        st.metric(
            "🚚 In Transit",
            f"{in_transit}"
        )

    with col4:
        st.metric(
            "⚠️ Delayed",
            f"{delayed}"
        )

    st.metric(
        "⏱️ Average Simulated ETA",
        f"{avg_eta:.1f} minutes"
    )

    st.divider()

    # ---------------------------------------------------
    # SECTION 2: DELIVERY MANAGEMENT
    # ---------------------------------------------------

    st.header("🚚 Delivery Management")

    st.write(
        "Filter deliveries to investigate operational "
        "conditions and delivery status."
    )

    filter1, filter2, filter3 = st.columns(3)

    with filter1:

        selected_drivers = st.multiselect(
            "Filter by Driver",
            options=sorted(deliveries["Driver"].unique()),
            default=sorted(deliveries["Driver"].unique())
        )

    with filter2:

        selected_statuses = st.multiselect(
            "Filter by Status",
            options=sorted(deliveries["Status"].unique()),
            default=sorted(deliveries["Status"].unique())
        )

    with filter3:

        selected_traffic = st.multiselect(
            "Filter by Traffic",
            options=sorted(deliveries["Traffic"].unique()),
            default=sorted(deliveries["Traffic"].unique())
        )

    max_distance = st.slider(
        "Maximum Delivery Distance (km)",
        min_value=1,
        max_value=40,
        value=40
    )

    filtered = deliveries[
        deliveries["Driver"].isin(selected_drivers)
        & deliveries["Status"].isin(selected_statuses)
        & deliveries["Traffic"].isin(selected_traffic)
        & (
            deliveries["Distance (km)"]
            <= max_distance
        )
    ].copy()

    st.caption(
        f"Showing {len(filtered)} of "
        f"{len(deliveries)} simulated deliveries."
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "📥 Download Filtered Deliveries",
        data=filtered.to_csv(index=False),
        file_name="etawise_filtered_deliveries.csv",
        mime="text/csv"
    )

    st.divider()

    # ---------------------------------------------------
    # SECTION 3: OPERATIONS ANALYTICS
    # ---------------------------------------------------

    st.header("📈 Operations Analytics")

    if filtered.empty:

        st.warning(
            "No deliveries match the selected filters. "
            "Adjust the filters to display analytics."
        )

    else:

        chart1, chart2 = st.columns(2)

        # Delivery status chart
        with chart1:

            status_counts = (
                filtered["Status"]
                .value_counts()
                .reset_index()
            )

            status_counts.columns = [
                "Status",
                "Deliveries"
            ]

            fig_status = px.pie(
                status_counts,
                names="Status",
                values="Deliveries",
                hole=0.55,
                title="Delivery Status Distribution"
            )

            fig_status.update_layout(
                height=380
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

        # Traffic chart
        with chart2:

            traffic_summary = (
                filtered.groupby("Traffic")[
                    "Estimated Time (min)"
                ]
                .mean()
                .reset_index()
            )

            fig_traffic = px.bar(
                traffic_summary,
                x="Traffic",
                y="Estimated Time (min)",
                title="Average ETA by Traffic Density",
                color="Traffic"
            )

            fig_traffic.update_layout(
                height=380,
                showlegend=False
            )

            st.plotly_chart(
                fig_traffic,
                use_container_width=True
            )

        chart3, chart4 = st.columns(2)

        # Driver workload
        with chart3:

            driver_counts = (
                filtered["Driver"]
                .value_counts()
                .reset_index()
            )

            driver_counts.columns = [
                "Driver",
                "Deliveries"
            ]

            fig_drivers = px.bar(
                driver_counts,
                x="Driver",
                y="Deliveries",
                title="Delivery Assignments by Driver"
            )

            fig_drivers.update_layout(
                height=380
            )

            st.plotly_chart(
                fig_drivers,
                use_container_width=True
            )

        # Distance vs ETA
        with chart4:

            fig_distance = px.scatter(
                filtered,
                x="Distance (km)",
                y="Estimated Time (min)",
                color="Traffic",
                hover_data=[
                    "Delivery ID",
                    "Driver",
                    "Status"
                ],
                title="Delivery Distance vs Estimated Time"
            )

            fig_distance.update_layout(
                height=380
            )

            st.plotly_chart(
                fig_distance,
                use_container_width=True
            )

    st.divider()

    # ---------------------------------------------------
    # SECTION 4: AI MODEL PERFORMANCE
    # ---------------------------------------------------

    st.header("🤖 AI Model Performance")

    st.write(
        "The following metrics represent the actual "
        "evaluation results from the trained ETAwise model."
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            "Mean Absolute Error",
            "3.09 min"
        )

    with metric2:
        st.metric(
            "Root Mean Squared Error",
            "3.87 min"
        )

    with metric3:
        st.metric(
            "R² Score",
            "0.8365"
        )

    with metric4:
        st.metric(
            "Baseline Improvement",
            "60.21%"
        )

    st.caption(
        "Metrics are from the held-out test set. "
        "The model was trained using a public "
        "food-delivery dataset."
    )

    # ---------------------------------------------------
    # ACTUAL VS PREDICTED
    # ---------------------------------------------------

    predictions = model_data["predictions"]

    if not predictions.empty:

        st.subheader("🎯 Actual vs Predicted Delivery Time")

        st.write(
            "Compare the model's predicted delivery durations "
            "with the actual values from the test dataset."
        )

        st.dataframe(
            predictions.head(10),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Showing the first 10 records from "
            "the exported test predictions."
        )

    else:

        st.warning(
            "test_predictions.csv was not found "
            "in the model folder."
        )

    st.divider()

    # ---------------------------------------------------
    # FEATURE IMPORTANCE
    # ---------------------------------------------------

    importance = model_data["importance"]

    st.subheader("🧠 What Influences ETA Predictions?")

    if not importance.empty:

        st.dataframe(
            importance.head(15),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Feature importance is based on the "
            "trained Random Forest model."
        )

    else:

        st.warning(
            "feature_importance.csv was not found "
            "in the model folder."
        )

    st.divider()

    # ---------------------------------------------------
    # MODEL LIMITATIONS
    # ---------------------------------------------------

    st.header("⚠️ Model Limitations")

    st.markdown(
        """
        - **Dataset:** The model was trained on food
          deliveries rather than package deliveries.

        - **Prediction range:** Random Forest models
          generally cannot extrapolate beyond the
          delivery durations represented in training.

        - **Live conditions:** Traffic, weather, and
          vehicle conditions are entered manually.
          Real-time integrations are not implemented.

        - **Prototype status:** Operational records
          are simulated, and predictions should not
          be interpreted as production-ready estimates.
        """
    )

    st.success(
        "ETAwise Administrator Dashboard loaded successfully!"
    )
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.predictor import predict_delivery_time


def show_consumer_page():

    st.title("📦 Consumer Portal")
    st.markdown("### Your Delivery, Explained.")

    st.write(
        "Adjust the delivery conditions and let ETAwise "
        "estimate how long your delivery will take."
    )

    st.divider()

    left, right = st.columns([1, 1], gap="large")

    # LEFT: Delivery conditions
    with left:

        st.subheader("🚚 Delivery Conditions")

        with st.form("delivery_estimator"):

            distance = st.number_input(
                "Delivery Distance (km)",
                min_value=0.1,
                max_value=100.0,
                value=10.0,
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

        # Run the model ONLY when Estimate is clicked
        if submitted:

            with st.spinner("Calculating your delivery estimate..."):

                # 1. Normal conditions
                normal_time = predict_delivery_time(
                    distance=distance,
                    traffic="Low",
                    weather="Sunny",
                    vehicle_condition="Average"
                )

                # 2. Apply selected traffic
                traffic_time = predict_delivery_time(
                    distance=distance,
                    traffic=traffic,
                    weather="Sunny",
                    vehicle_condition="Average"
                )

                # 3. Apply selected weather
                weather_time = predict_delivery_time(
                    distance=distance,
                    traffic=traffic,
                    weather=weather,
                    vehicle_condition="Average"
                )

                # 4. Apply selected vehicle condition
                final_time = predict_delivery_time(
                    distance=distance,
                    traffic=traffic,
                    weather=weather,
                    vehicle_condition=vehicle_condition
                )

                # Calculate adjustments
                traffic_effect = traffic_time - normal_time
                weather_effect = weather_time - traffic_time
                vehicle_effect = final_time - weather_time

                # Save results
                st.session_state.consumer_inputs = {
                    "distance": distance,
                    "traffic": traffic,
                    "weather": weather,
                    "vehicle_condition": vehicle_condition,
                    "normal_time": normal_time,
                    "traffic_effect": traffic_effect,
                    "weather_effect": weather_effect,
                    "vehicle_effect": vehicle_effect,
                    "prediction": final_time
                }

    # RIGHT: Prediction results
    with right:

        st.subheader("⏱️ Your Delivery Estimate")

        if "consumer_inputs" in st.session_state:

            inputs = st.session_state.consumer_inputs

            st.success("AI prediction generated!")

            st.metric(
                label="Estimated Delivery Duration",
                value=f"{inputs['prediction']:.1f} minutes"
            )

            st.divider()

            st.markdown("### 🔍 Understanding Your Estimate")

            st.write(
                "ETAwise compares your selected delivery conditions "
                "with a standard delivery scenario to explain "
                "how the predicted duration changes."
            )

            # Prediction breakdown
            breakdown = pd.DataFrame({
                "Factor": [
                    "☀️ Normal Conditions",
                    f"🚦 Traffic: {inputs['traffic']}",
                    f"🌦️ Weather: {inputs['weather']}",
                    f"🚗 Vehicle: {inputs['vehicle_condition']}",
                    "📦 Final Prediction"
                ],
                "Minutes": [
                    inputs["normal_time"],
                    inputs["traffic_effect"],
                    inputs["weather_effect"],
                    inputs["vehicle_effect"],
                    inputs["prediction"]
                ]
            })

            st.dataframe(
                breakdown.style.format({"Minutes": "{:+.1f}"}),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "The first row is the standard-condition estimate. "
                "The middle rows show changes in predicted minutes. "
                "The final row is the resulting delivery estimate."
            )

            st.divider()

            # Waterfall chart
            st.markdown("### 📊 How Conditions Affect Your ETA")

            fig = go.Figure(go.Waterfall(
                orientation="v",
                measure=[
                    "absolute",
                    "relative",
                    "relative",
                    "relative",
                    "total"
                ],
                x=[
                    "Normal",
                    "Traffic",
                    "Weather",
                    "Vehicle",
                    "Final ETA"
                ],
                y=[
                    inputs["normal_time"],
                    inputs["traffic_effect"],
                    inputs["weather_effect"],
                    inputs["vehicle_effect"],
                    0
                ],
                text=[
                    f"{inputs['normal_time']:.1f}",
                    f"{inputs['traffic_effect']:+.1f}",
                    f"{inputs['weather_effect']:+.1f}",
                    f"{inputs['vehicle_effect']:+.1f}",
                    f"{inputs['prediction']:.1f}"
                ],
                textposition="outside",
                connector={"line": {"color": "#AFC5E5"}},
                increasing={"marker": {"color": "#FF6B6B"}},
                decreasing={"marker": {"color": "#4ECCA3"}},
                totals={"marker": {"color": "#69B7FF"}}
            ))

            fig.update_layout(
                title="Delivery Time Breakdown",
                yaxis_title="Minutes",
                showlegend=False,
                height=420,
                paper_bgcolor="#101C40",
                plot_bgcolor="#101C40",
                font={"color": "white"},
                margin=dict(l=20, r=20, t=60, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.caption(
                "These adjustments show how the AI model responds "
                "to different conditions. They are not guaranteed "
                "causal effects, and the individual adjustments "
                "depend on the order in which conditions are applied."
            )

            st.divider()

            # Selected conditions
            st.markdown("### 📋 Selected Delivery Conditions")

            st.write(f"📍 Distance: {inputs['distance']} km")
            st.write(f"🚦 Traffic: {inputs['traffic']}")
            st.write(f"🌦️ Weather: {inputs['weather']}")
            st.write(
                f"🚗 Vehicle Condition: "
                f"{inputs['vehicle_condition']}"
            )

        else:

            st.info(
                "Adjust the delivery conditions and "
                "click Estimate Delivery Time to begin."
            )
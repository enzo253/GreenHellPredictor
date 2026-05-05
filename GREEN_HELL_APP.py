import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from together import Together
import plotly.express as px
import json
import re

load_dotenv()

railway_key = os.getenv("MY_CAR_KEY")
together_key = os.getenv("TOGETHER_API")

client = Together(api_key=together_key)

# ----------------------------
# SAFE JSON PARSER
# ----------------------------
def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Invalid JSON from model")


# ----------------------------
# DB LOAD
# ----------------------------
conn = psycopg2.connect(railway_key)
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM car_info
    JOIN car_specs ON car_info.id = car_specs.id
""")

info = cursor.fetchall()
conn.close()

cars_df = pd.DataFrame(info, columns=[
    "car_info_id", "car", "driver", "lap_time", "power_weight",
    "car_specs_id","Top speed", "Car type", "Curb weight", "Power",
    "Est. max acceleration","0 - 40 kph", "0 - 50 kph", "0 - 60 kph",
    "0 - 80 kph","0 - 100 kph", "0 - 120 kph", "0 - 130 kph",
    "0 - 140 kph"
])

# FORCE NUMERIC
numeric_cols = [
    "Top speed", "Curb weight", "Power", "Est. max acceleration",
    "0 - 40 kph","0 - 50 kph","0 - 60 kph","0 - 80 kph",
    "0 - 100 kph","0 - 120 kph","0 - 130 kph","0 - 140 kph"
]
cars_df[numeric_cols] = cars_df[numeric_cols].apply(pd.to_numeric, errors="coerce")

st.title("GREEN HELL PREDICTOR")
st.subheader("CAR SELECTOR")

selected_car_name = st.selectbox("Select Car:", cars_df["car"].unique())

cars_clean_df = cars_df.drop(columns=["car_info_id", "car_specs_id", "lap_time"])
car_specs = cars_clean_df[cars_clean_df["car"] == selected_car_name].copy().head(1)

missing_features = car_specs.columns[car_specs.isnull().any()].tolist()

# ----------------------------
# CAR 1 PREDICTION
# ----------------------------
if len(missing_features) > 0:

    prompt = f"""
Return ONLY valid JSON.

Rules:
- no text
- no markdown
- only JSON

Car:
{car_specs.to_json()}

Missing:
{missing_features}
"""

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V4-Pro",
        messages=[
            {"role": "system", "content": "Output ONLY JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    try:
        predicted_values = safe_json_load(response.choices[0].message.content)

        car_specs = car_specs.astype(object)

        for feature, value in predicted_values.items():
            try:
                car_specs.at[car_specs.index[0], feature] = float(value)
            except:
                car_specs.at[car_specs.index[0], feature] = None

    except Exception as e:
        st.error(f"Car 1 prediction error: {e}")

st.write(car_specs)

# ----------------------------
# VIEW SELECTOR
# ----------------------------
st.sidebar.header("Performance Metrics")
selected_view = st.sidebar.radio(
    "Select an option:",
    ["AI Prediction", "📊 Performance Analysis", "Car Comparisons"]
)

# ----------------------------
# AI PREDICTION
# ----------------------------
if selected_view == "AI Prediction":

    prompt_ai = f"""
Predict Nürburgring performance for:

{car_specs.to_json()}
"""

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V4-Pro",
        messages=[{"role": "user", "content": prompt_ai}]
    )

    st.write(response.choices[0].message.content)

# ----------------------------
# PERFORMANCE ANALYSIS
# ----------------------------
acceleration_features = [
    '0 - 40 kph','0 - 50 kph','0 - 60 kph','0 - 80 kph',
    '0 - 100 kph','0 - 120 kph','0 - 130 kph','0 - 140 kph'
]

car_specs_acceleration = car_specs[acceleration_features].dropna(axis=1)
car_specs_long = car_specs_acceleration.transpose().reset_index()
car_specs_long.columns = ['Speed', 'Time']

if selected_view == "📊 Performance Analysis":

    fig = px.scatter_3d(
        car_specs,
        x="Power",
        y="Curb weight",
        z="0 - 100 kph",
        color="car"
    )
    st.plotly_chart(fig)

# ----------------------------
# CAR COMPARISON
# ----------------------------
if selected_view == "Car Comparisons":

    selected_car_name_1 = st.selectbox(
        "Select Second Car:",
        cars_df["car"].unique(),
        key="car2"
    )

    car_specs_1 = cars_clean_df[cars_clean_df["car"] == selected_car_name_1].copy().head(1)

    missing_features_1 = car_specs_1.columns[car_specs_1.isnull().any()].tolist()

    # FIXED CONDITION
    if len(missing_features_1) > 0:

        prompt2 = f"""
Return ONLY JSON.

Car:
{car_specs_1.to_json()}

Missing:
{missing_features_1}
"""

        response_1 = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Pro",
            messages=[
                {"role": "system", "content": "Output ONLY JSON."},
                {"role": "user", "content": prompt2}
            ],
            temperature=0.2
        )

        try:
            predicted_values_1 = safe_json_load(response_1.choices[0].message.content)

            car_specs_1 = car_specs_1.astype(object)

            for feature, value in predicted_values_1.items():
                try:
                    car_specs_1.at[car_specs_1.index[0], feature] = float(value)
                except:
                    car_specs_1.at[car_specs_1.index[0], feature] = None

        except Exception as e:
            st.error(f"Car 2 prediction error: {e}")

    st.write(car_specs_1)
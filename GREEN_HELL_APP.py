import streamlit as st
import pandas as pd
import psycopg2
import os 
from dotenv import load_dotenv
import requests
from together import Together 
import plotly.express as px
import json

load_dotenv()

railway_key = os.getenv("MY_CAR_KEY")
together_key = os.getenv("TOGETHER_API")

client = Together(api_key=together_key)


conn = psycopg2.connect(railway_key)
cursor = conn.cursor()

cursor.execute('''
    SELECT * FROM car_info
    JOIN car_specs ON car_info.id = car_specs.id
''')
info = cursor.fetchall()
conn.close()


cars_df = pd.DataFrame(info, columns = ["car_info_id", "car", "driver", "lap_time", "power_weight",
    "car_specs_id","Top speed", "Car type", "Curb weight", "Power", "Est. max acceleration",
    "0 - 40 kph", "0 - 50 kph", "0 - 60 kph", "0 - 80 kph",
    "0 - 100 kph", "0 - 120 kph", "0 - 130 kph", "0 - 140 kph"])

st.title("GREEN HELL PREDICTOR")
st.subheader("CAR SELECTOR")

selected_car_name = st.selectbox("Select Car:", cars_df["car"].unique())
cars_clean_df = cars_df.drop(columns=["car_info_id", "car_specs_id", "lap_time"])
car_specs = cars_clean_df[cars_clean_df["car"] == selected_car_name].copy()
car_specs = car_specs.head(1)
missing_features = car_specs.columns[car_specs.isnull().any()].tolist()


if missing_features:
    prompt_missing_values = f"""
    You are a senior automotive analyst specializing in car performance and specifications.

    **Task:** Predict the missing values (NaN) for the specified features using the provided car data.

    **Instructions:**  
    - You MUST return a **valid JSON object ONLY**, without any extra text, explanations, or formatting.
    - The JSON must have:
        - **Keys** = feature names  
        - **Values** = predicted numbers (float or int).
    - **You must fill EVERY missing feature with a predicted numerical value.**  
    - **Do not return "nan" under any circumstances.**
    - If information is insufficient, **make the best reasonable numerical estimate based on available data and general automotive knowledge.**
    - **Do not add any extra text before or after the JSON.**  
    - **Do not format output as markdown, code blocks, or natural language. Only raw JSON.**

    **Available Car Data:**  
    {car_specs.to_json()}

    **Missing Features:**  
    {missing_features}

    **Strict Output Example:**
    {{
      "feature1": 123.4,
      "feature2": 85.0,
      "feature3": 567
    }}
    """
 
    response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt_missing_values}]
        )

 
    try:
        predicted_values = json.loads(response.choices[0].message.content)


        for feature, value in predicted_values.items():
            if isinstance(value, (int, float)):  # If it's already numeric, use it
                    car_specs.at[car_specs.index[0], feature] = float(value)
            elif isinstance(value, str) and value.strip().lower() == "nan":  # If the value is "nan" (string)
                    car_specs.at[car_specs.index[0], feature] = None  # Or np.nan
            else:
                try:
                    car_specs.at[car_specs.index[0], feature] = float(value)
                except ValueError:
                    car_specs.at[car_specs.index[0], feature] = None
        
    except json.JSONDecodeError:
        st.error("Error: AI response is not in expected JSON format.")


st.write(car_specs)

st.sidebar.header("Performance Metrics")
selected_view = st.sidebar.radio(
    "Select an option:",
    ["AI Prediction", "📊 Performance Analysis", "Car Comparisons"]
)


if selected_view == "AI Prediction":
    prompt_ai_prediction = f"""
    Given the following specifications for the {selected_car_name}:  
    {car_specs.to_json()}  

    Predict the Nürburgring lap time and other key performance characteristics of the car, excluding any historical lap times.
    """

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt_ai_prediction}]
    )

    ai_response = response.choices[0].message.content
    st.write("### Car Details:")
    st.write(ai_response)

acceleration_features = ['0 - 40 kph', '0 - 50 kph', '0 - 60 kph', '0 - 80 kph', '0 - 100 kph', '0 - 120 kph', '0 - 130 kph', '0 - 140 kph']
car_specs_acceleration = car_specs[acceleration_features].dropna(axis=1)

car_specs_acceleration_long = car_specs_acceleration.transpose().reset_index()
car_specs_acceleration_long.columns = ['Speed (kph)', 'Acceleration Time (seconds)']

numeric_columns = ['Top speed', 'Curb weight', 'Power']
performance_values = car_specs[numeric_columns].values.flatten()
labels = numeric_columns
streamlit_bg_color = st.get_option("theme.backgroundColor")


acceleration_score = 1000 / car_specs[acceleration_features].sum(axis=1).values[0]
curb_weight_score = car_specs['Curb weight'].values[0] / 100
power_score = car_specs['Power'].values[0] / 100
TopSpeed_score = car_specs['Top speed'].values[0] / 10


if selected_view == "📊 Performance Analysis":
    if not car_specs.empty:
        fig = px.scatter_3d(
        car_specs, 
        x="Power", 
        y="Curb weight", 
        z="0 - 100 kph", 
        color="car", 
        size="power_weight",
        hover_data=["car", "Top speed"],
        title="3D Performance Comparison"
        )
        st.plotly_chart(fig)

        fig_speed_vs_power = px.scatter(
        car_specs,
        x="Power",
        y="0 - 100 kph",
        color="car",
        size="power_weight",
        hover_data=["car", "Top speed"],
        title=f"Power vs Speed for {selected_car_name}"
        )
        st.plotly_chart(fig_speed_vs_power)

        fig3 = px.line(
        car_specs_acceleration_long,
        x='Speed (kph)', 
        y='Acceleration Time (seconds)', 
        title=f"Acceleration Time vs Speed for {selected_car_name}",
        labels={'Speed (kph)': 'Speed (kph)', 'Acceleration Time (seconds)': 'Acceleration Time (seconds)'}
        )

        st.plotly_chart(fig3)

        fig_radar = px.line_polar(
        r=performance_values,
        theta=labels,
        line_close=True,
        title=f"Performance Radar Chart for {selected_car_name}"
        )

        fig_radar.update_layout(
            polar=dict(
            bgcolor="black",
                radialaxis=dict(
                    visible=True,
                    color='white', 
                    showticklabels=True,  
                    tickfont=dict(color='white')  
                ),
                angularaxis=dict(
                    visible=True,
                    color='white',
                    showticklabels=True,
                    tickfont=dict(color='white') 
                )
            ),
            plot_bgcolor=streamlit_bg_color,
            paper_bgcolor=streamlit_bg_color,  
            title_font=dict(color='white'), 
            font=dict(color='white')  
        )

        fig_radar.update_traces(fillcolor=streamlit_bg_color)

        st.plotly_chart(fig_radar)

    else:
        st.error("No data found for the selected car.")

if selected_view == "Car Comparisons":

    selected_car_name_1 = st.selectbox("Select Second Car:", cars_df["car"].unique(), key="car_selector_1")
    car_specs_1 = cars_clean_df[cars_clean_df["car"] == selected_car_name_1].copy()
    car_specs_1 = car_specs_1.head(1)
    missing_features_1 = car_specs_1.columns[car_specs_1.isnull().any()].tolist()

    if missing_features: 
        prompt_missing_values_1 = f"""
        You are a senior automotive analyst specializing in car performance and specifications.

        **Task:** Predict the missing values (NaN) for the specified features using the provided car data.

        **Instructions:**  
        - You MUST return a **valid JSON object ONLY**, without any extra text, explanations, or formatting.
        - The JSON must have:
        - **Keys** = feature names  
        - **Values** = predicted numbers (float or int).
        - **You must fill EVERY missing feature with a predicted numerical value.**  
        - **Do not return "nan" under any circumstances.**
        - If information is insufficient, **make the best reasonable numerical estimate based on available data and general automotive knowledge.**
        - **Do not add any extra text before or after the JSON.**  
        - **Do not format output as markdown, code blocks, or natural language. Only raw JSON.**

    **Available Car Data:**  
    {car_specs_1.to_json()}

    **Missing Features:**  
    {missing_features_1}

    **Strict Output Example:**
    {{
      "feature1": 123.4,
      "feature2": 85.0,
      "feature3": 567
    }}
    """
 
        response_1 = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt_missing_values_1}]
        )

 
        try:
            predicted_values_1 = json.loads(response_1.choices[0].message.content)


            for feature, value in predicted_values_1.items():
                if isinstance(value, (int, float)):  # If it's already numeric, use it
                    car_specs_1.at[car_specs_1.index[0], feature] = float(value)
                elif isinstance(value, str) and value.strip().lower() == "nan":  # If the value is "nan" (string)
                    car_specs_1.at[car_specs_1.index[0], feature] = None  # Or np.nan
            else:
                try:
                    car_specs_1.at[car_specs_1.index[0], feature] = float(value)
                except ValueError:
                    car_specs_1.at[car_specs_1.index[0], feature] = None
        
        except json.JSONDecodeError:
            st.error("Error: AI response is not in expected JSON format.")

    st.write(car_specs_1)

    acceleration_score_1 = 1000 / car_specs_1[acceleration_features].sum(axis=1).values[0]
    curb_weight_score_1 = car_specs_1['Curb weight'].values[0] / 100
    power_score_1 = car_specs_1['Power'].values[0] / 100
    TopSpeed_score_1 = car_specs_1['Top speed'].values[0] / 10


    car_specs_score_01 = pd.DataFrame({
        'Metric': ['acceleration score', 'curb weight score', 'power score', 'top speed score'],
        'Score': [acceleration_score_1, curb_weight_score_1, power_score_1, TopSpeed_score_1],
        'car': selected_car_name_1
    })

    car_specs_score_02 = pd.DataFrame({
        'Metric': ['acceleration score', 'curb weight score', 'power score', 'top speed score'],
        'Score': [acceleration_score, curb_weight_score, power_score, TopSpeed_score],
        'car': selected_car_name
    })

    combined_scores = pd.concat([car_specs_score_01, car_specs_score_02], axis=0)

    fig = px.bar(
        combined_scores, 
        x='Metric', 
        y='Score', 
        color='car',
        barmode='group',
        title="Car Comparison: Performance Scores"
    )
    st.plotly_chart(fig)
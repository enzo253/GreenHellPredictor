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
    You are an expert in car performance analysis. The following car has missing values (NaN). 

    **Task:** Predict only the missing values for these specific features based on the car's available data.  
    - **Return your response in JSON format** (keys: feature names, values: predicted numbers or "nan").  
    - **Do not include any explanations or extra text.**  

    Car Specifications:
    {car_specs.to_json()}

    Missing Features:
    {missing_features}

    Expected Output:
    {{
        "feature1": value1,
        "feature2": value2,
        ...
    }}
    """

 
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt_missing_values}]
    )

 
    try:
        predicted_values = json.loads(response.choices[0].message.content)


        for feature, value in predicted_values.items():
            if feature in car_specs.columns and pd.isna(car_specs[feature].values[0]):
                car_specs.at[car_specs.index[0], feature] = float(value) if value != "nan" else None
    except json.JSONDecodeError:
        st.error("Error: AI response is not in expected JSON format.")


st.write(car_specs)

st.sidebar.header("Performance Metrics")
selected_view = st.sidebar.radio(
    "Select an option:",
    ["AI Prediction", "📊 Performance Analysis"]
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
        y="0 - 100 kph",  # You can change the speed metric if you want
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
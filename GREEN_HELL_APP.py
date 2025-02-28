import streamlit as st
import pandas as pd
import psycopg2
import os 
from dotenv import load_dotenv
import requests
from together import Together 

load_dotenv()

railway_key = os.getenv("MY_CAR_KEY")
together_key = os.getenv("TOGETHER_API")

client = Together(api_key = together_key)


conn = psycopg2.connect(railway_key)
cursor = conn.cursor()

cursor.execute('''
    SELECT * FROM car_info
    JOIN car_specs ON car_info.id = car_specs.id
''')

info = cursor.fetchall()

for row in info:
    print(row)

conn.close()

cars_df = pd.DataFrame(info, columns = ["car_info_id", "car", "driver", "lap_time", "power_weight",
    "car_specs_id","Top speed", "Car type", "Curb weight", "Est. max acceleration",
    "0 - 40 kph", "0 - 50 kph", "0 - 60 kph", "0 - 80 kph",
    "0 - 100 kph", "0 - 120 kph", "0 - 130 kph", "0 - 140 kph"])


st.title("GREEN HELL PREDICTOR")

st.subheader("CAR SELECTOR")

selected_car = st.selectbox("Select Car:", cars_df["car"].unique())

cars_df = cars_df.drop(columns=["car_info_id", "car_specs_id", "lap_time"])

car_specs = cars_df[cars_df["car"] == selected_car]

car_specs_str = car_specs.to_string(index=False)

prompt = f"Given the following specifications for the {selected_car}: {car_specs}. Based solely on this data, predict the Nürburgring lap time and other key performance characteristics of the car, excluding any historical lap times."

response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    messages=[{"role": "user", "content": prompt}]
)

ai_response = response.choices[0].message.content

st.write("### Car Details:")
st.write(cars_df[cars_df["car"] == selected_car])
st.write(ai_response)



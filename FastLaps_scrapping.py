from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import psycopg2
from datetime import timedelta
import pandas as pd
from together import Together 

load_dotenv()

railway_key = os.getenv("MY_CAR_KEY")

print(railway_key)

def get_data():
    url = "https://fastestlaps.com/tracks/nordschleife"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    rows = soup.find_all("tr")

    for text in rows:

        columns = text.find_all("td")
        car_info = [col.get_text(strip=True) for col in columns]

        if len(car_info) == 5:
            position = car_info[0]
            car = car_info[1]
            driver = car_info[2]
            lap_time = car_info[3]
            power_weight = car_info[4]

            data.append({"car": car, "driver": driver, "lap_time": lap_time, "power_weight": power_weight})

    return data

def get_car_specs(car_links):
    data = []

    acceleration_keys = [
        "Top speed", "Car type", "Curb weight", "Power", "Est. max acceleration", "0 - 40 kph", "0 - 50 kph", "0 - 60 kph",
        "0 - 80 kph", "0 - 100 kph", "0 - 120 kph",
        "0 - 130 kph", "0 - 140 kph"
    ]

    for src in car_links:
        url = src[1]  
        response = requests.get(url, timeout=10)  
        soup = BeautifulSoup(response.text, "html.parser")

        specs = soup.find_all("table", class_="table fl-datasheet")

        car_info = {}

        for table in specs:
            rows = table.find_all("tr")

            for row in rows:
                cols = row.find_all("td")

                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)

                    car_info[key] = value


        acceleration_data = {
            key: car_info.get(key, None)
            for key in acceleration_keys
        }

        if acceleration_data:
            data.append(acceleration_data)

    return data

def clean_data(fast_laps, car_specs):
    
    fast_laps_df = pd.DataFrame(fast_laps, columns=["car", "driver", "lap_time", "power_weight"])
    car_specs_df = pd.DataFrame(car_specs, columns=[
        "Top speed", "Car type", "Curb weight", "Power","Est. max acceleration", "0 - 40 kph", "0 - 50 kph", "0 - 60 kph",
        "0 - 80 kph", "0 - 100 kph", "0 - 120 kph",
        "0 - 130 kph", "0 - 140 kph"
    ])

    acceleration_cols = [
        "0 - 40 kph", "0 - 50 kph", "0 - 60 kph",
        "0 - 80 kph", "0 - 100 kph", "0 - 120 kph",
        "0 - 130 kph", "0 - 140 kph"
    ]

    car_specs_df[acceleration_cols] = (
        car_specs_df[acceleration_cols]
        .astype(str)
        .replace({"None": None, "nan": None, "": None})
        .apply(lambda col: col.str.replace("s", "", regex=False))
        .apply(pd.to_numeric, errors="coerce")
    )

    fast_laps_df["lap_time"] = fast_laps_df["lap_time"].replace({"None": None, "": None})    
    fast_laps_df["lap_time"] = pd.to_timedelta("00:" + fast_laps_df["lap_time"])

    fast_laps_df["lap_time"] = fast_laps_df["lap_time"].apply(lambda x: str(x))

    fast_laps_df["power_weight"] = fast_laps_df["power_weight"].apply(
        lambda x: (
            float(x.split("/")[0].strip()) / float(x.split("/")[1].strip()) 
            if isinstance(x, str) and "/" in x
            and x.split("/")[0].strip() not in ['-', ''] 
            and x.split("/")[1].strip() not in ['-', ''] 
            and float(x.split("/")[1].strip()) != 0
            else None
        )
    )

    car_specs_df['Top speed'] = car_specs_df["Top speed"].str.extract(r"(\d+)")
    car_specs_df["Est. max acceleration"] = car_specs_df["Est. max acceleration"].str.extract(r"(\d+\.\d+)")
    car_specs_df["Curb weight"] = car_specs_df["Curb weight"].str.extract(r"(\d+)")
    car_specs_df["Power"] = car_specs_df["Power"].str.extract(r"(\d+)")

    car_specs_df["Est. max acceleration"] = car_specs_df["Est. max acceleration"].astype(float)
    car_specs_df["Top speed"] = car_specs_df["Top speed"].astype(float)
    car_specs_df["Curb weight"] = car_specs_df["Curb weight"].astype(float)
    car_specs_df["Power"] = car_specs_df["Power"].astype(float)


    print(car_specs_df.head())
 
    return fast_laps_df, car_specs_df

def save_to_database(fast_laps_df, car_specs_df, railway_key):
    try:
        conn = psycopg2.connect(railway_key)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS car_info CASCADE")
        cursor.execute("DROP TABLE IF EXISTS car_specs CASCADE")

        cursor.execute('''CREATE TABLE IF NOT EXISTS car_info (
            id SERIAL PRIMARY KEY,
            car VARCHAR(255),
            driver VARCHAR(255),
            lap_time TEXT,
            power_weight FLOAT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS car_specs (
            id SERIAL PRIMARY KEY,
            "Top speed" FLOAT, 
            "Car type" TEXT, 
            "Curb weight" FlOAT,
            "Power" FLOAT,
            "Est. max acceleration" FLOAT, 
            "0 - 40 kph" FLOAT, 
            "0 - 50 kph" FLOAT, 
            "0 - 60 kph" FLOAT,
            "0 - 80 kph" FLOAT, 
            "0 - 100 kph" FLOAT, 
            "0 - 120 kph" FLOAT,
            "0 - 130 kph" FLOAT, 
            "0 - 140 kph" FLOAT
        )''')


        fast_laps_records = fast_laps_df.to_records(index=False).tolist()
        car_specs_records = car_specs_df.to_records(index=False).tolist()


        if fast_laps_records:
            insert_query = '''INSERT INTO car_info (car, driver, lap_time, power_weight) 
                              VALUES (%s, %s, %s, %s)'''
            cursor.executemany(insert_query, fast_laps_records)
        

        if car_specs_records:
            insert_query = '''INSERT INTO car_specs ("Top speed", "Car type", "Curb weight", "Power", 
                                                     "Est. max acceleration", "0 - 40 kph", 
                                                     "0 - 50 kph", "0 - 60 kph", "0 - 80 kph", 
                                                     "0 - 100 kph", "0 - 120 kph", 
                                                     "0 - 130 kph", "0 - 140 kph") 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.executemany(insert_query, car_specs_records)

        conn.commit()
        print("Data saved successfully!")

    except Exception as e:
        print(f"Data did not save. Error: {e}")

    finally:
        conn.close()

cleaned_data = clean_data(fast_laps, car_specs)

print(cleaned_data)

fast_laps_df, car_specs_df = clean_data(fast_laps, car_specs)

print(f"Fast Laps DataFrame size: {fast_laps_df.shape}")
print(f"Car Specs DataFrame size: {car_specs_df.shape}")

data_saving = save_to_database(fast_laps_df, car_specs_df, railway_key)

print(data_saving)
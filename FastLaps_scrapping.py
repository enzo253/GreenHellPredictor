from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

load_dotenv()

railway_key = os.getenv("MY_RAILWAY_KEY")

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
            data.append((position, car, driver, lap_time, power_weight))

    return data

fast_laps = get_data()

print(fast_laps)

BASE_URL = "https://fastestlaps.com"

def get_car_links():

    url = BASE_URL + "/tracks/nordschleife"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")
    data = []

    for row in rows:

        car_column = row.find_all("td")

        for link in car_column:
            references = link.find("a")

            if references and references.has_attr("href"):
                car_name = references.get_text(strip=True)
                car_links = references.get("href")
                full_link = BASE_URL + car_links
                data.append((car_name, full_link))

    return data

def get_car_specs(car_links):
    data = []

    acceleration_keys = [
        "Top speed", "Car type", "Curb weight", "Est. max acceleration", "0 - 40 kph", "0 - 50 kph", "0 - 60 kph",
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


        acceleration_data = {}
        for key in acceleration_keys:
            if key in car_info:
                acceleration_data[key] = car_info[key]

            else:
                acceleration_data[key] = "N/A"


        if acceleration_data:
            data.append(acceleration_data)

    return data


car_links = get_car_links()
print("Car Links:", car_links)

car_specs = get_car_specs(car_links)
print("Car Specs:", car_specs)

#def save_to_database():

#conn = psycopg2.connect(MY_RAILWAY_KEY)
#cursor = conn.cursor()

#cursor.execute('''CREATE TABLE IF DOES NOT EXSIST car_info (
#) '''


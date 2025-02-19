from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

load_dotenv()

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

    for src in car_links:
        url = src[1]  
        response = requests.get(url, timeout=10)  
        soup = BeautifulSoup(response.text, "html.parser")

        specs = soup.find_all("table", class_="table fl-datasheet")

        for table in specs:
            rows = table.find_all("tr")

            car_info = []
            for row in rows:
                cols = row.find_all("td")

                for col in cols:
                    span = col.find("span")
                    if span:
                        car_info.append(span.get_text(strip=True))

                        if len(car_info) >= 36:
                            weight = car_info[0]
                            fuel_consumption = car_info[1]
                            emissions = car_info[2]
                            zero_100kph = car_info[3]
                            zero_200kph = car_info[4]
                            zero_300kph = car_info[5]
                            hundred_200kph = car_info[7]
                            two_hundred_300kph = car_info[9]
                            estimated_quarter_mile = car_info[15]
                            estimated_half_mile = car_info[17]
                            top_speed = car_info[19]
                            max_acceleration = car_info[21]
                            engine_capacity = car_info[22]
                            power_output = car_info[23]
                            torque = car_info[30]
                            price_eur = car_info[34]
                            price_usd = car_info[35]

                            data.append((
                            weight, fuel_consumption, emissions, zero_100kph, zero_200kph, zero_300kph,
                            hundred_200kph, two_hundred_300kph, estimated_quarter_mile, estimated_half_mile,
                            top_speed, max_acceleration, engine_capacity, power_output, torque,
                            price_eur, price_usd
                            ))
    return data

car_links = get_car_links()
print("Car Links:", car_links)

car_specs = get_car_specs(car_links)
print("Car Specs:", car_specs)












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


#def get_car_build():


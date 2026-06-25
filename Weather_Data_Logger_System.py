import requests
import mysql.connector
import json
from datetime import datetime
import os
import logging

#logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
     handlers=[
        logging.FileHandler("WeatherDataLoggerSystem.log"),
        logging.StreamHandler()
    ])
print("Current Directory:", os.getcwd())
logging.info("Program Started")
# Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="M@ha",
        database="weather_db"
    )
#Check weather
def check_weather():
    API_KEY="0194a46b790a48818ec20041261906"
    city=input("Enter city ")
    logging.info(f"User searched for city: {city}")
    url=f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    try:
        response=requests.get(url)
        data = response.json()
        
#print(data)
        if "location" in data:
            city_name = data["location"]["name"]
            country = data["location"]["country"]
            temp = data["current"]["temp_c"]
            humidity = data["current"]["humidity"]
            wind_speed = data["current"]["wind_kph"]
            condition = data["current"]["condition"]["text"]
            feels_like = data["current"]["feelslike_c"]
            pressure = data["current"]["pressure_mb"]
            visibility = data["current"]["vis_km"]
            uv_index = data["current"]["uv"]

            print("Weather Report")
            print("City        :", city_name)
            print("Country     :", country)
            print("Temperature :", temp, "°C")
            print("Humidity    :", humidity, "%")
            print("Wind Speed  :", wind_speed, "km/h")
            print("Condition   :", condition)
            print("UV Index    :", uv_index)
            

            conn = get_connection()
            cursor = conn.cursor()

            query="""insert into weather_reports(
city,country,temperature,humidity,wind_speed,
weather_condition,feels_like,pressure,visibility,
uv_index,search_date,search_time,raw_response)
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            values=(
    data["location"]["name"],
    data["location"]["country"],
    data["current"]["temp_c"],
    data["current"]["humidity"],
    data["current"]["wind_kph"],
    data["current"]["condition"]["text"],
    data["current"]["feelslike_c"],
    data["current"]["pressure_mb"],
    data["current"]["vis_km"],
    data["current"]["uv"],          # UV Index
    datetime.now().date(),
    datetime.now().time(),
    json.dumps(data)
) 
            logging.info(f"Weather data fetched successfully for {city_name}")
            # Save data to database
            cursor.execute(query,values)
            conn.commit()
            logging.info(f"Weather report stored in database for {city_name}")
            print("Weather data saved successfully!")
            cursor.close()
            conn.close()
        else:
            error_msg = data.get("error", {}).get("message", "City not found")
            logging.warning(f"Weather API Error: {error_msg}")
            print("Error:", error_msg)
    except Exception as e:
        logging.error(f"Error while fetching weather: {e}")
        print("Error:", e)
def view_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        logging.info("User viewed weather history")
        cursor.execute("""
        SELECT id, city, temperature,
               weather_condition,
               search_date, search_time
        FROM weather_reports
        """)
        records = cursor.fetchall()
        logging.info(f"Retrieved {len(records)} records from database")
        print("\nWeather History")
    
        for row in records:
            print(row)

        cursor.close()
        conn.close()

    except Exception as e:
        logging.error(f"Error while viewing history: {e}")
        print("Error:", e)
def view_last_search():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT city, temperature,
               weather_condition,
               search_date, search_time
        FROM weather_reports
        ORDER BY id DESC
        LIMIT 1
    """)

    record = cursor.fetchone()

    if record:
        print("\nLast Weather Search")
        print(record)
    else:
        print("No records found")

    cursor.close()
    conn.close()

# Main Menu
while True:

    print("\n WEATHER DATA LOGGER")
    print("1. Check Weather")
    print("2. View Weather History")
    print("3. View Last Weather Search")
    print("4. Exit")

    choice = input("Enter Choice: ")
    logging.info(f"Menu choice selected: {choice}")

    if choice == "1":
        check_weather()

    elif choice == "2":
        view_history()

    elif choice == "3":
        view_last_search()

    elif choice == "4":
        logging.info("Application closed by user")
        print("Thank You!")
        break

    else:
        logging.warning("Invalid menu choice entered")
        print("Invalid Choice")
   
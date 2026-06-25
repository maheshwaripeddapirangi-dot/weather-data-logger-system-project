import requests
import mysql.connector
import json
from datetime import datetime
import os
import logging

# ==========================
# LOGGING SETUP
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    handlers=[
        logging.FileHandler("WeatherDataLoggerSystem.log"),
        logging.StreamHandler()
    ]
)

print("Current Directory:", os.getcwd())
logging.info("Program Started")

# ==========================
# DATABASE CONNECTION
# ==========================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="M@ha",   # change if needed
        database="weather_db"
    )

# ==========================
# CHECK WEATHER
# ==========================
def check_weather():
    API_KEY = "YOUR_API_KEY"  # replace with your WeatherAPI key
    city = input("Enter city: ")
    logging.info(f"User searched for city: {city}")

    url = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

    try:
        response = requests.get(url)
        data = response.json()

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

            print("\n🌦️ Weather Report")
            print("City        :", city_name)
            print("Country     :", country)
            print("Temperature :", temp, "°C")
            print("Humidity    :", humidity, "%")
            print("Wind Speed  :", wind_speed, "km/h")
            print("Condition   :", condition)
            print("UV Index    :", uv_index)

            conn = get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO weather_reports (
                city, country, temperature, humidity, wind_speed,
                weather_condition, feels_like, pressure, visibility,
                uv_index, search_date, search_time, raw_response
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                city_name,
                country,
                temp,
                humidity,
                wind_speed,
                condition,
                feels_like,
                pressure,
                visibility,
                uv_index,
                datetime.now().date(),
                datetime.now().time(),
                json.dumps(data)
            )

            cursor.execute(query, values)
            conn.commit()

            logging.info(f"Weather data stored for {city_name}")
            print("✅ Data saved successfully!")

            cursor.close()
            conn.close()

        else:
            error_msg = data.get("error", {}).get("message", "City not found")
            logging.warning(f"API Error: {error_msg}")
            print("Error:", error_msg)

    except Exception as e:
        logging.error(f"Error: {e}")
        print("Error:", e)

# ==========================
# VIEW HISTORY
# ==========================
def view_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, city, temperature, weather_condition,
                   search_date, search_time
            FROM weather_reports
        """)

        records = cursor.fetchall()

        print("\n📊 Weather History:")
        for row in records:
            print(row)

        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

# ==========================
# LAST SEARCH
# ==========================
def view_last_search():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT city, temperature, weather_condition,
               search_date, search_time
        FROM weather_reports
        ORDER BY id DESC
        LIMIT 1
    """)

    record = cursor.fetchone()

    if record:
        print("\n📌 Last Weather Search:")
        print(record)
    else:
        print("No records found")

    cursor.close()
    conn.close()

# ==========================
# MAIN MENU
# ==========================
while True:
    print("\n===== WEATHER DATA LOGGER =====")
    print("1. Check Weather")
    print("2. View History")
    print("3. View Last Search")
    print("4. Exit")

    choice = input("Enter Choice: ")
    logging.info(f"Menu choice: {choice}")

    if choice == "1":
        check_weather()
    elif choice == "2":
        view_history()
    elif choice == "3":
        view_last_search()
    elif choice == "4":
        print("Thank You!")
        break
    else:
        print("Invalid Choice")
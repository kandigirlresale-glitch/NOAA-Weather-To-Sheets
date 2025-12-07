import requests
import gspread
import json
import os
from datetime import datetime

# --- Configuration ---
# Your NOAA API Key (NWS API sometimes just needs a good User-Agent, but key is good practice)
NOAA_API_KEY = "efLTKyQXEgUUYizWcgfUwMBMRCUeJQyP" 

# NWS Gridpoint Forecast URL (Example for a specific point in NJ)
API_URL = "api.weather.gov" 

# Name of the Google Sheet you created
SHEET_NAME = "NOAA Weather Data" 
# Name of the specific tab/worksheet within that sheet
WORKSHEET_TITLE = "Weather_Data" 

# --- Google Sheets Setup ---
# The script will read credentials from the environment variable set by GitHub Actions
# to create the local credentials.json file.
CREDENTIALS_FILE = 'credentials.json'

# --- Fetch NOAA Data ---
def fetch_weather_data():
    # NOAA/NWS API requires a descriptive User-Agent header
    headers = {
        'User-Agent': 'MyCustomWeatherApp/1.0 (contact@example.com)',
        'Accept': 'application/ld+json' 
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status() 
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# --- Process and Upload Data ---
def update_google_sheet():
    # Connect to Google Sheets
    try:
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        sh = gc.open(SHEET_NAME).worksheet(WORKSHEET_TITLE)
        print("Successfully connected to Google Sheets.")
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        print("Ensure credentials.json is created correctly by the GitHub Action and sheet is shared.")
        exit()

    weather_data = fetch_weather_data()
    if not weather_data:
        return

    print("Fetching data from NWS API...")

    periods = weather_data['properties']['periods']
    
    headers = ['Run Time', 'Start Time', 'Temperature (F)', 'Forecast', 'Daytime']
    data_to_upload = [headers]
    
    current_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for period in periods:
        row = [
            current_run_time,
            period['startTime'],
            period['temperature'],
            period['shortForecast'],
            'Yes' if period['isDaytime'] else 'No'
        ]
        data_to_upload.append(row)

    sh.clear() 
    sh.update(data_to_upload) 
    print(f"Successfully uploaded {len(periods)} weather records to Google Sheets '{SHEET_NAME}' tab '{WORKSHEET_TITLE}'.")

if __name__ == "__main__":
    update_google_sheet()

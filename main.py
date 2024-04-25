import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv('api_key.env')

# Replace `<api-key>` with your actual API key
api_key_historical = os.getenv('API_KEY_HISTORICAL')
api_key_forecast = os.getenv('API_KEY_FORECAST')

# Base URLs for historical and forecast data
base_url_hist = "https://dmigw.govcloud.dk/v2/metObs/collections/observation/items"
base_url_forecast = "https://dmigw.govcloud.dk/v1/forecastedr/collections/harmonie_dini_sf/position"

# Date ranges for historical and forecast data
dates_hist = [
    ("2019-08-01T00:00:00+02:00", "2019-08-09T00:00:00+02:00"),
    ("2020-08-01T00:00:00+02:00", "2020-08-09T00:00:00+02:00"),
    ("2021-08-01T00:00:00+02:00", "2021-08-09T00:00:00+02:00")
]
date_forecast = "2024-04-26T00:00:00+02:00/2024-04-28T00:00:00+02:00"

# Function to fetch and process data
def fetch_data(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['features']
    else:
        print(f"Failed to fetch data with params: {params}")
        return []

# Fetch historical data
observations = []
for start_date, end_date in dates_hist:
    params = {'api-key': api_key_historical, 'datetime': f"{start_date}/{end_date}", 'limit': 1000}
    features = fetch_data(base_url_hist, params)
    for feature in features:
        obs = feature['properties']
        obs.update({
            'latitude': feature['geometry']['coordinates'][1],
            'longitude': feature['geometry']['coordinates'][0]
        })
        observations.append(obs)

# Fetch forecast data
params_forecast = {
    'api-key': api_key_forecast,
    'coords': 'POINT(12.561 55.715)',
    'crs': 'crs84',
    'parameter-name': 'temperature-2m,wind-speed-10m',
    'datetime': date_forecast,
    'f': 'GeoJSON'
}
forecast_data = fetch_data(base_url_forecast, params_forecast)

# Process historical data into DataFrame
df_hist = pd.DataFrame(observations)
df_hist['observed'] = pd.to_datetime(df_hist['observed']).dt.tz_localize(None)
df_hist['created'] = pd.to_datetime(df_hist['created']).dt.tz_localize(None)
df_hist_pivot = df_hist.pivot_table(index=['observed', 'stationId', 'latitude', 'longitude', 'created'],
                                    columns='parameterId', values='value', aggfunc='first').reset_index()

# Process forecast data into DataFrame
df_forecast = pd.DataFrame([{
    **feat['properties'],
    'latitude': feat['geometry']['coordinates'][1],
    'longitude': feat['geometry']['coordinates'][0],
    'step': feat['properties'].get('step')
} for feat in forecast_data])

# Save DataFrames to CSV
df_hist_pivot.to_csv('historical_weather_data.csv', index=False, sep=';')
df_forecast.to_csv('forecast_weather_data.csv', index=False, sep=";")

print("Historical data saved to 'historical_weather_data.csv'")
print("Forecast data saved to 'forecast_weather_data.csv'")

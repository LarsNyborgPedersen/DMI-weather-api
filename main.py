import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv('api_key.env')  # Load environment variables from .env file

# Replace `<api-key>` with your actual API key
#api_key = "3a38d6e6-2dfa-4e77-b261-6ba0d61974e5"
api_key = os.getenv('API_KEY')
base_url = "https://dmigw.govcloud.dk/v2/metObs/collections/observation/items"

# Define the dates for which you want to fetch weather data
dates = [
    ("2019-08-01T00:00:00+02:00", "2019-08-09T00:00:00+02:00"),
    ("2020-08-01T00:00:00+02:00", "2020-08-09T00:00:00+02:00"),
    ("2021-08-01T00:00:00+02:00", "2021-08-09T00:00:00+02:00")
]

# Prepare a list to hold all observations
observations = []

# Loop through each date range
for start_date, end_date in dates:
    params = {
        'api-key': api_key,
        'datetime': f"{start_date}/{end_date}",
        'limit': 1000  # Adjust limit as needed, considering the API's max limit
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        for feature in data.get('features', []):
            obs = feature['properties']
            obs['latitude'] = feature['geometry']['coordinates'][1]
            obs['longitude'] = feature['geometry']['coordinates'][0]
            observations.append(obs)
    else:
        print(f"Failed to fetch data for {start_date} to {end_date}")

# Create a DataFrame
df = pd.DataFrame(observations)

# Convert the 'observed' column to datetime format
df['observed'] = pd.to_datetime(df['observed'])

# Display the DataFrame
print(df)

# Convert the 'observed' column to datetime format and remove timezone information
df['observed'] = pd.to_datetime(df['observed']).dt.tz_localize(None)

# Save the DataFrame to an Excel file, overriding any existing file
excel_file_path = 'weather_data.xlsx'
df.to_excel(excel_file_path, index=False, engine='openpyxl')

print(f"Data saved to {excel_file_path}")
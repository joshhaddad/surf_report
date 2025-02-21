import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class SurfReport:
    def __init__(self):
        self.api_key = os.getenv('STORMGLASS_API_KEY')
        self.base_url = 'https://api.stormglass.io/v2'

    def get_forecast(self, lat, lng, start, end):
        endpoint = f'{self.base_url}/weather/point'
        params = {
            'lat': lat,
            'lng': lng,
            'params': 'waveHeight,wavePeriod,windSpeed,windDirection',  # Simplified!
            'start': start.isoformat(),
            'end': end.isoformat()
        }
        headers = {'Authorization': self.api_key}
        
        try:
            print(f"Making request to: {endpoint}")
            print(f"With params: {params}")
            response = requests.get(endpoint, params=params, headers=headers)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            return self._parse_conditions(response.json())
        except Exception as e:
            print(f"Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response content: {e.response.text}")
            return None

    def _parse_conditions(self, data):
        try:
            forecasts = []
            for hour in data['hours']:
                forecasts.append({
                    'time': datetime.strptime(hour['time'], '%Y-%m-%dT%H:%M:%S+00:00'),
                    'wave_height': hour['waveHeight']['noaa'],
                    'wave_period': hour['wavePeriod']['noaa'],
                    'wind_speed': hour['windSpeed']['noaa'],
                    'wind_direction': hour['windDirection']['noaa']
                })
            return forecasts
        except KeyError as e:
            print(f"Error parsing data: {e}")
            return None

def get_direction_text(degrees):
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]

def get_surf_rating(wave_height, wave_period, wind_speed, wind_direction):
    score = 0
    
    # Wave height scoring
    if 2 <= wave_height <= 4:
        score += 3
    elif 1 <= wave_height <= 5:
        score += 2
    elif wave_height > 0:
        score += 1
        
    # Wave period scoring
    if wave_period >= 10:
        score += 3
    elif wave_period >= 7:
        score += 2
    elif wave_period > 0:
        score += 1
        
    # Wind scoring
    if 247.5 <= wind_direction <= 292.5:  # West winds
        if wind_speed < 15:
            score += 3
        else:
            score += 1
    elif wind_speed < 5:  # Light winds
        score += 2
        
    if score >= 7:
        return "🟢 Epic"
    elif score >= 5:
        return "🟡 Good"
    elif score >= 3:
        return "🟠 Fair"
    else:
        return "🔴 Poor"

def main():
    location = {
        'name': 'The Washout, Folly Beach',
        'lat': 32.6541,
        'lng': -79.9387
    }
    
    now = datetime.now()
    start_time = now.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=24)
    
    reporter = SurfReport()
    forecasts = reporter.get_forecast(
        location['lat'], 
        location['lng'],
        start_time,
        end_time
    )
    
    if forecasts:
        print(f"\n🏄‍♂️ Surf Report for {location['name']} 🌊")
        print(f"Forecast for next 24 hours")
        
        for forecast in forecasts:
            time_str = forecast['time'].strftime('%I:%M %p')
            print(f"\nTime: {time_str}")
            print(f"Wave Height: {forecast['wave_height']:.1f}ft")
            print(f"Wave Period: {forecast['wave_period']:.1f}s")
            wind_dir_text = get_direction_text(forecast['wind_direction'])
            print(f"Wind: {forecast['wind_speed']:.1f}mph from {wind_dir_text}")
            rating = get_surf_rating(
                forecast['wave_height'],
                forecast['wave_period'],
                forecast['wind_speed'],
                forecast['wind_direction']
            )
            print(f"Rating: {rating}")

if __name__ == "__main__":
    main()
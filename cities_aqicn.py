import requests
from const import API_TOKEN, STATIONS

def get_air_quality_by_city(city, token=API_TOKEN):
    """
    Fetch air quality data for a given city from the AQICN API.

    Args:
        city (str): Name of the city (e.g., 'beijing', 'london').
        token (str): Your AQICN API token.

    Returns:
        dict: Air quality data if successful, None otherwise.
    """
    base_url = f"https://api.waqi.info/feed/{city}/?token={token}"

    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise error for bad HTTP status
        data = response.json()

        if data.get('status') == 'ok':
            return data['data']
        else:
            print(f"Error from API: {data.get('data')}")
            return None

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_air_quality_by_station(stations, token=API_TOKEN):
    """
    Fetch air quality data for a list of stations from the AQICN API.

    Args:
        stations (list): List of station names (e.g., ['station1', 'station2']).
        token (str): Your AQICN API token.

    Returns:
        dict: A dictionary with station names as keys and their air quality data as values.
    """
    results = {}
    for station in stations:
        base_url = f"https://api.waqi.info/feed/{station}/?token={token}"
        try:
            response = requests.get(base_url)
            response.raise_for_status()  # Raise error for bad HTTP status
            data = response.json()

            if data.get('status') == 'ok':
                results[station] = data['data']
            else:
                print(f"Error from API for station {station}: {data.get('data')}")
                results[station] = None

        except requests.RequestException as e:
            print(f"Request error for station {station}: {e}")
            results[station] = None

    return results

if __name__ == "__main__":    

    # Example usage
    city = 'A476599'  # Replace with the desired city name
    air_quality = get_air_quality_by_station(stations=STATIONS)

    if air_quality:
        print(air_quality)
    else:
        print("Failed to retrieve air quality data.")

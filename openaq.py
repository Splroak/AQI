import requests

base_url = f"https://api.waqi.info/map/bounds?token=d533e23a5ecca2b4ae57df4fc07adf6c7e32c806&latlng=21.0285,106.0308,20.8485,105.8048"
response = requests.get(base_url)
response.raise_for_status()  # Raise error for bad HTTP status
data = response.json()
print(data)

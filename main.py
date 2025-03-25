import network
import urequests
import ujson
import time

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PWD"
LATITUDE = "LOCATION_LATITUDE"
LONGITUDE = "LOCATION_LONGITUDE"
URL = "" 
WEATHER_CODES = {}

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(1)
    if wlan.status() != 3:
        return False
    else:
        return True

def get_weather():
    try:
        response = urequests.get(URL)
        if response.status_code == 200:
            weather_json = ujson.loads(response.text)
            current_time = time.localtime()
            year, month, day, hour, _, _, _, _ = current_time
            formatted_time = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:00"
            weather_code = 0
            wc_index = [h for h in weather_json["hourly"]["time"]].index(hours)
            weather_code = weather_json["hourly"]["weather_code"][wc_index]
            return WEATHER_CODES[str(weather_code)]
        else:
            return f"Error: Unable to retrieve weather data (status code: {response.status_code}, message: {response.text})"
    except Exception as e:
        return f"Error: {e}"
    finally:
        if 'response' in locals():
            response.close()

with open('config') as conf_file:
    config = ujson.load(conf_file)
    WIFI_SSID = config["WIFI_SSID"]
    WIFI_PASSWORD = config["WIFI_PASSWORD"]
    LATITUDE = config["LATITUDE"]
    LONGITUDE = config["LONGITUDE"]
    URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m,weather_code&timezone=auto&forecast_days=1"

if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    print("WiFi connected")
    with open('weather_codes.json') as data_file:
        WEATHER_CODES = ujson.loads(data_file.read())
    while True:
        weather_info = get_weather()
        print(weather_info)
        time.sleep(1800)
else:
    print("WiFi connection failed")
    exit(1)
exit(0)

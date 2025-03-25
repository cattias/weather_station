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
            year, month, day, hour, minute, second, weekday, yearday = current_time
            formatted_time = "{:04d}-{:02d}-{:02d}T{:02d}:00".format(year, month, day, hour)
            weather_code = 0
            wc_index = 0
            for hours in weather_json["hourly"]["time"]:
                if hours == formatted_time:
                    break
                wc_index += 1
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
    config = ujson.loads(conf_file.read())
    WIFI_SSID = config["WIFI_SSID"]
    WIFI_PASSWORD = config["WIFI_PASSWORD"]
    LATITUDE = config["LATITUDE"]
    LONGITUDE = config["LONGITUDE"]
    URL = f"https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&hourly=temperature_2m,weather_code&timezone=auto&forecast_days=1" % (LATITUDE, LONGITUDE)

if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    print("WiFi connected")
    with open('weather_codes.json') as data_file:
        WEATHER_CODES = ujson.loads(data_file.read())
    weather_info = get_weather()
    print(weather_info)
else:
    print("WiFi connection failed")
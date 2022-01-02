# ReadMe
# Sends an email alert if it's "nice" outside
# Dependencies: requests (pip install requests), secureData (my internal function to grab nonpublic variables from a secure folder)
# Note: weatherAPIKey should be obtained for free through openweathermap.org.

import requests
import datetime
import time
import mail
from decimal import Decimal as d
import random
import sys
import pwd
import os
from securedata import securedata

userDir = pwd.getpwuid(os.getuid())[0]

lat = securedata.getItem("latitude")
lon = securedata.getItem("longitude")


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(
        now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def shiftLocation(location):
    if(random.randrange(2) == 1):
        return d(location) + d(random.randrange(10000000)/100000000)
    else:
        return d(location) - d(random.randrange(10000000)/100000000)


def getBikeLink():
    return f"https://www.google.com/maps/dir//{shiftLocation(lat)},{shiftLocation(lon)}"


def convertTemperature(temp):
    return round((temp - 273.15) * 9/5 + 32)


# context variables
plantyStatus = securedata.getItem("planty", "status")
now = datetime.datetime.now()

# Call API
url_request = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={securedata.getItem('weather', 'api_key')}"
response = requests.get(url_request).json()

temperature = convertTemperature(response["current"]["temp"])
conditions_now = response["current"]["weather"][0]["description"]
conditions_now_icon = response["current"]["weather"][0]["icon"]
conditions_tomorrow = response["daily"][1]["weather"][0]["description"]
high_tomorrow = convertTemperature(response["daily"][0]["temp"]["max"])
low_tomorrow = convertTemperature(response["daily"][1]["temp"]["min"])
sunrise_tomorrow_formatted = time.strftime('%Y-%m-%d %H:%M AM', time.localtime(response["daily"][1]["sunrise"]))
sunset_tomorrow_formatted = time.strftime('%Y-%m-%d %I:%M PM', time.localtime(response["daily"][1]["sunset"]))

high = convertTemperature(response["daily"][0]["temp"]["max"])
wind = response["current"]["wind_speed"]
sunset = response["daily"][0]["sunset"]
timeToSunset = (sunset - time.time()) / 3600

# set WEATHER_DATA
weatherData = {
    "current_temperature": temperature,
    "current_conditions": conditions_now,
    "current_conditions_icon": conditions_now_icon,
    "tomorrow_high": high_tomorrow,
    "tomorrow_low": low_tomorrow,
    "tomorrow_conditions": conditions_tomorrow,
    "tomorrow_sunrise": sunrise_tomorrow_formatted,
    "tomorrow_sunset": sunset_tomorrow_formatted}

securedata.setItem("weather", "data", weatherData)
    
if(securedata.getItem("weather", "alert_walk_sent") < (time.time() - 43200) and now.hour >= 10):
    if(((temperature >= 65 and temperature <= 85) or (high >= 72 and high <= 90)) and wind < 10 and timeToSunset > 2):
        message = f"""\
            Hi Tyler,\
                <br><br>Get walking, biking, and moving!<br><br>
                <ul>
                    <li>It's {temperature}° right now with a high of {high}°- what a promising day to get outside!</li>
                    <li>It's not raining</li>
                    <li>The wind isn't bad</li>
                    <li>It's a nice time of day</li>
                    <br><br><h2><a href='{getBikeLink()}'>Here's a random place for you to go.</a></h2>"""

        mail.send("Particularly good weather today!", message)
        securedata.setItem("weather", "alert_walk_sent", int(time.time()))
        securedata.log("Walk Alert Sent")

plantyAlertSent = securedata.getItem("weather", "alert_planty_sent")
plantyAlertChecked = securedata.getItem("weather", "alert_planty_checked")

if(len(sys.argv) > 1 and sys.argv[1] == 'force' or (not plantyAlertSent or not plantyAlertChecked or (int(plantyAlertSent) < (time.time() - 43200) and int(plantyAlertChecked) < (time.time() - 21600)))):
    securedata.log(f"Checked Planty ({plantyStatus}): low {low_tomorrow}, high {high}")
    securedata.setItem("weather", "alert_planty_checked", int(time.time()))
    if(low_tomorrow < 55 and plantyStatus == "out"):
        try:
            mail.send("Take Planty In", f"Hi Tyler,<br><br>The low tonight is {low_tomorrow}°. Please take Planty in!", to=','.join(securedata.getItem("weather", "alert_planty_emails")))
            securedata.setItem("planty", "status", "in")
            securedata.setItem("weather", "alert_planty_sent", int(time.time()))
        except Exception as e:
            securedata.log(f"Could not send Planty email: {e}", level="error")
    if((high > 80 or low_tomorrow >= 56) and plantyStatus == "in"):
        try:
            mail.send("Take Planty Out", f"Hi Tyler,<br><br>It looks like a nice day! It's going to be around {high}°. Please take Planty out.""", to=','.join(securedata.getItem("weather", "alert_planty_emails")))
            securedata.setItem("planty", "status", "out")
            securedata.setItem("weather", "alert_planty_sent", int(time.time()))
        except Exception as e:
            securedata.log(f"Could not send Planty email: {e}", level="error")

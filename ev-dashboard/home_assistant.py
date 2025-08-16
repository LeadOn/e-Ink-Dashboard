import logging
import RPi.GPIO as GPIO
import time
import requests
import os
import json
from datetime import datetime, timedelta


from dotenv import load_dotenv
from gpio_init import setLedColors
from screen_management import screenInit, screenToSleep, drawHaLoadingScreen, drawHaErrorScreen, haPartialUpdate

load_dotenv()

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")
HA_BATTERY_ENTITY = os.getenv("HA_BATTERY_ENTITY")
HA_CHARGE_STATUS = os.getenv("HA_CHARGE_STATUS")
HA_CAR_TEMP = os.getenv("HA_CAR_TEMP")

CLEAR_SCREEN_BTN = 26
API_BTN = 16

def haHomeScreen():
    time.sleep(1)
    syncTime = None

    while True:
        if syncTime is None or syncTime + timedelta(seconds=10) < datetime.now():
            logging.info("Displaying Home Assistant screen...")
            setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)
            screenInit(True, False, False)

            # Drawing loading screen
            drawHaLoadingScreen()

            # Showing loading indicator
            setLedColors(GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)

            # Getting battery level
            logging.info("Getting battery level from Home Assistant...")
            batteryStatus = getEntityStatusFromHa(HA_BATTERY_ENTITY)

            if batteryStatus['code'] == 200:
                jsonBody = json.loads(batteryStatus['rawBody'])
                logging.info("Received battery status: " + jsonBody['state'])
                haPartialUpdate(0, 40, "Battery: " + jsonBody['state'] + "%", True)
                setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

                # Getting charge status
                setLedColors(GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
                logging.info("Getting charge status from Home Assistant...")
                chargeStatus = getEntityStatusFromHa(HA_CHARGE_STATUS)

                if chargeStatus['code'] == 200:
                    jsonBody = json.loads(chargeStatus['rawBody'])
                    logging.info("Received charge status: " + jsonBody['state'])
                    haPartialUpdate(0, 60, "Charge: " + jsonBody['state'], False)
                    setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

                    # Getting car temp
                    setLedColors(GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
                    logging.info("Getting car temperature from Home Assistant...")
                    carTemp = getEntityStatusFromHa(HA_CAR_TEMP)

                    if carTemp['code'] == 200:
                        jsonBody = json.loads(carTemp['rawBody'])
                        logging.info("Received car temperature: " + jsonBody['state'])
                        haPartialUpdate(0, 80, "Temperature: " + jsonBody['state'] + '°C', False)
                        setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)
                    
                    else:
                        drawHaErrorScreen(carTemp['code'])
                        setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)
                
                else:
                    drawHaErrorScreen(chargeStatus['code'])
                    setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)

            else:
                drawHaErrorScreen(batteryStatus['code'])
                setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)

            # Don't forget to put the screen to sleep when done
            screenToSleep()

            syncTime = datetime.now()

        if GPIO.input(CLEAR_SCREEN_BTN) == GPIO.LOW:
            logging.info("Exiting!")
            break;
        
        if GPIO.input(API_BTN) == GPIO.LOW:
            logging.info("Forcing refresh...")
            syncTime = datetime.now() + timedelta(days=-10)

        time.sleep(0.1)

def getEntityStatusFromHa(entityName):
    logging.info("Getting '" + entityName + " status from '" + HA_URL + "'...")
    
    url = HA_URL + "/api/states/" + entityName

    headers = {
        'Authorization': 'Bearer ' + HA_TOKEN
    }

    response = requests.request("GET", url, headers=headers)

    return {
        'code': response.status_code,
        'rawBody': response.text
    }
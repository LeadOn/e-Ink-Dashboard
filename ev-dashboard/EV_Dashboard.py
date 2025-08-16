#!/usr/bin/python

import sys
import os

import logging
import time
import requests
from waveshare_epd import epd2in13_V4
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO

# Defining ports
BLUE_LED = 2
GREEN_LED = 3
RED_LED = 4
CLEAR_SCREEN_BTN = 26
API_BTN = 16
DHT_11 = 19


# Defining e-ink screen stuff
epd = epd2in13_V4.EPD()
font15 = ImageFont.truetype('./pic/Font.ttc', 15)
font24 = ImageFont.truetype('./pic/Font.ttc', 24)
isSleeping = False
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame 

logging.basicConfig(level=logging.DEBUG)

def readActionButtons():
    if GPIO.input(CLEAR_SCREEN_BTN) == GPIO.LOW:
        logging.info("Clear screen btn pressed!")
        clearScreen()

    if GPIO.input(API_BTN) == GPIO.LOW:
        logging.info("API btn pressed!")
        getApiData()

def setLedColors(red, green, blue):
    GPIO.output(BLUE_LED, blue)
    GPIO.output(GREEN_LED, green)
    GPIO.output(RED_LED, red)

def gpioInit():
    logging.info("Initializing GPIO ports...");
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initializing LEDs
    GPIO.setup(BLUE_LED, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(GREEN_LED, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RED_LED, GPIO.OUT, initial=GPIO.HIGH)

    # Initializing button
    GPIO.setup(CLEAR_SCREEN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(API_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def screenInit(clear = True, showWelcomeScreen = False, goToSleep = True):
    setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)

    logging.info("Initializing screen...")
    epd.init()
    global isSleeping
    isSleeping = False

    if clear == True:
        logging.info("Clearing screen...")
        epd.Clear(0xFF)

    if showWelcomeScreen == True:
        logging.info("Showing welcome screen...")   
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), 'LeadOn\'s e-Ink POC', font = font15, fill = 0)
        draw.line([(0, 20),(400,20)], fill = 0,width = 1)
        draw.text((0, 40), 'Display initialized.', font = font15, fill = 0)
        epd.display(epd.getbuffer(image))
        setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

    if goToSleep == True:
        screenToSleep()

def clearScreen():
    logging.info("Clearing screen...")
    screenInit(True, False, True)

def screenToSleep():
    global isSleeping
    
    if isSleeping == False:
        logging.info("Putting screen to sleep...")
        epd.sleep()
        setLedColors(GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        isSleeping = True
    else:
        logging.info("Already sleeping!")

def getApiData():
    screenInit(True, True, False)

    setLedColors(GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)

    # partial update
    logging.info("Getting data from SWAPI...")
    epd.displayPartBaseImage(epd.getbuffer(image))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 40, 400, 80), fill = 255)
    draw.text((0, 40), 'Getting data from SWAPI...', font = font15, fill = 0)
    epd.displayPartial(epd.getbuffer(image))

    url = f"https://swapi.info/api/films/1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

    # partial update
    logging.info("Parsing data...")
    epd.displayPartBaseImage(epd.getbuffer(image))
    draw.rectangle((0, 40, 400, 80), fill = 255)
    draw.text((0, 40), 'Parsing data...', font = font15, fill = 0)
    epd.displayPartial(epd.getbuffer(image))

    logging.info("Showing API result (film " + data['title'] + ")...")
    image2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame    
    draw2 = ImageDraw.Draw(image2)
    draw2.text((0, 0), 'LeadOn\'s e-Ink POC', font = font15, fill = 0)
    draw2.line([(0, 20),(400,20)], fill = 0,width = 1)
    draw2.text((0, 40), 'Film: ' + data["title"], font = font15, fill = 0)
    draw2.text((0, 60), 'Directed by: ' + data["director"], font = font15, fill = 0)
    epd.displayPartial(epd.getbuffer(image2)) 

    screenToSleep()

try:
    gpioInit()
    screenInit(True, True, True)

    while True:
        readActionButtons()
        time.sleep(0.1)
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
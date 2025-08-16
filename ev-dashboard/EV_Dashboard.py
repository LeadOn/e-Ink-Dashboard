#!/usr/bin/python

import sys
import os

import logging
import time
import requests
import RPi.GPIO as GPIO

from waveshare_epd import epd2in13_V4
from gpio_init import gpioInit, setLedColors
from screen_management import screenInit, screenToSleep, clearScreen
from home_assistant import haHomeScreen

CLEAR_SCREEN_BTN = 26
API_BTN = 16

try:
    # Initializing GPIO ports
    logging.info("Initializing GPIO ports...")
    gpioInit()

    # Initializing screen
    screenInit(True, True, True)

    while True:
        if GPIO.input(CLEAR_SCREEN_BTN) == GPIO.LOW:
            logging.info("Exiting!")
            clearScreen()
            screenToSleep()
            epd2in13_V4.epdconfig.module_exit(cleanup=True)
            break;
        
        if GPIO.input(API_BTN) == GPIO.LOW:
            logging.info("Going to HA home...")
            haHomeScreen()
            screenInit(True, True, True)
            time.sleep(1)
        
        time.sleep(0.1)
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
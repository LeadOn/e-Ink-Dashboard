import RPi.GPIO as GPIO

# Defining ports
BLUE_LED = 2
GREEN_LED = 3
RED_LED = 4
CLEAR_SCREEN_BTN = 26
API_BTN = 16

def gpioInit():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initializing LEDs
    GPIO.setup(BLUE_LED, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(GREEN_LED, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RED_LED, GPIO.OUT, initial=GPIO.HIGH)

    # Initializing button
    GPIO.setup(CLEAR_SCREEN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(API_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def setLedColors(red, green, blue):
    GPIO.output(BLUE_LED, blue)
    GPIO.output(GREEN_LED, green)
    GPIO.output(RED_LED, red)
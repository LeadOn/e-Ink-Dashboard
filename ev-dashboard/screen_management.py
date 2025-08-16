import RPi.GPIO as GPIO
import logging

from waveshare_epd import epd2in13_V4
from PIL import Image,ImageDraw,ImageFont
from gpio_init import setLedColors

# Logging set to debug, in order to monitor if everything is working fine
logging.basicConfig(level=logging.DEBUG)

epd = epd2in13_V4.EPD()
font15 = ImageFont.truetype('./pic/Font.ttc', 15)
font24 = ImageFont.truetype('./pic/Font.ttc', 24)

# Defining e-ink screen stuff
isSleeping = False
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame 

def screenInit(clear = True, showWelcomeScreen = False, goToSleep = True):
    setLedColors(GPIO.HIGH, GPIO.LOW, GPIO.LOW)

    epd.init()
    global isSleeping
    isSleeping = False

    if clear == True:
        logging.info("Clearing screen...")
        epd.Clear(0xFF)

    if showWelcomeScreen == True:
        logging.info("Showing welcome screen...")
        global image 
        image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame 
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), 'LeadOn\'s dashboard', font = font15, fill = 0)
        draw.line([(0, 20),(400,20)], fill = 0,width = 1)
        draw.text((0, 40), 'Left: Exit', font = font15, fill = 0)
        draw.text((0, 60), 'Right: EV Dashboard', font = font15, fill = 0)
        draw.text((0, 100), 'Make a choice!', font = font15, fill = 0)
        epd.display(epd.getbuffer(image))
        setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

    if goToSleep == True:
        screenToSleep()

def screenToSleep():
    global isSleeping
    
    if isSleeping == False:
        logging.info("Putting screen to sleep...")
        epd.sleep()
        setLedColors(GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        isSleeping = True
    else:
        logging.info("Already sleeping!")

def clearScreen():
    logging.info("Clearing screen...")
    screenInit(True, False, True)

def drawHaLoadingScreen():
    logging.info("Drawing Home Assistant loading screen...")
    global image
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame 

    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'LeadOn\'s Mokka-E', font = font15, fill = 0)
    draw.line([(0, 20),(400,20)], fill = 0,width = 1)
    draw.text((0, 40), 'Loading data...', font = font15, fill = 0)
    draw.text((0, 60), 'Loading data...', font = font15, fill = 0)
    draw.text((0, 80), 'Loading data...', font = font15, fill = 0)
    epd.display(epd.getbuffer(image))

    logging.info("Screen ready!");

    setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

def drawHaErrorScreen(error):
    logging.info("Drawing Home Assistant error screen...")

    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'LeadOn\'s Mokka-E', font = font15, fill = 0)
    draw.line([(0, 20),(400,20)], fill = 0,width = 1)
    draw.text((0, 40), 'Error while getting data:', font = font15, fill = 0)
    draw.text((0, 60), error, font = font15, fill = 0)
    epd.display(epd.getbuffer(image))

    setLedColors(GPIO.LOW, GPIO.HIGH, GPIO.LOW)

def haPartialUpdate(x, y, text, refresh):
    global image

    if refresh == True:
        epd.displayPartBaseImage(epd.getbuffer(image))

    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, 400, y + 20), fill = 255)
    draw.text((x, y), text, font = font15, fill = 0)
    epd.displayPartial(epd.getbuffer(image))
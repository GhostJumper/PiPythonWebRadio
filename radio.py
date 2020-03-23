#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  radio.py

import subprocess
import sys
import os
picdir = '/home/pi/Radio/pic'
libdir = '/home/pi/Radio/lib'
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
from gpiozero import Button
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

file = open("./stations.txt", "r")
stations = []
for line in file:
    strippedLine = line.rstrip()
    stations.append(strippedLine.split(' - '))
    

logging.basicConfig(level=logging.DEBUG)

cursorPoint = 0
isRadioPlaying = False


key1 = Button(5)
key2 = Button(6)
key3 = Button(13)
key4 = Button(19)

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)

epd = epd2in7.EPD()
epd.init()


def displayUI(himageFromCursor):
    try:
        epd.Clear(0xFF)

        Himage = himageFromCursor
        draw = ImageDraw.Draw(Himage)
        for idx,station in enumerate(stations):
            draw.text((10, idx*15), str(station[0]), font = font18, fill = 0)
        epd.display(epd.getbuffer(Himage))

        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        logging.info("Clear...")
        epd.Clear(0xFF)
        logging.info("Goto Sleep...")
        epd.sleep()
        epd2in7.epdconfig.module_exit()
        exit()

def displayCursor():
    try:
        Himage = Image.new('1', (epd.height, epd.width), 255) # 255: clear the frame 
        draw = ImageDraw.Draw(Himage)
        draw.text((0, 15*cursorPoint), ">", font = font18, fill = 0)
        displayUI(Himage)
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        logging.info("Clear...")
        epd.Clear(0xFF)
        logging.info("Goto Sleep...")
        epd.sleep()
        epd2in7.epdconfig.module_exit()
        exit()
    
        
def cursorUp():
    global cursorPoint
    if (cursorPoint-1<0):
        cursorPoint=len(stations)-1
    else:
        cursorPoint -= 1
    displayCursor()

def cursorDown():
    global cursorPoint
    if (cursorPoint+1>len(stations)-1):
        cursorPoint = 0
    else:
        cursorPoint += 1
    displayCursor()
    
def killRadio():
    global isRadioPlaying
    if(isRadioPlaying):
        print("Radio was killed")
        killCommand = "pkill mpv"
        process = subprocess.Popen(killCommand.split(), stdout=subprocess.PIPE)
        isRadioPlaying = False
    else:
        print("No radio running to be killed")
        
    
def startRadio():
    time.sleep(2)
    global isRadioPlaying
    killRadio()
    isRadioPlaying = True
    bashCommand = "mpv " + stations[cursorPoint][1]
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

    
key1.when_pressed = cursorUp
key2.when_pressed = cursorDown
key3.when_pressed = startRadio
key4.when_pressed = killRadio

displayCursor()

for station in stations:
    print station
    
while True:
    pass

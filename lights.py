#include all necessary packages to get LEDs to work with Raspberry Pi
import time
import board
import neopixel


def goal_light():

    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=1)
    
    i = 0
    
    strip.fill((255, 0, 0))
    time.sleep(2)
    strip.fill((0,0,0))
    time.sleep(1)
    
    for x in range(0, LED_COUNT):
        strip[x] = (255,0,0)
    
    while i < 10:
        strip.fill((255, 0, 0))
        time.sleep(.25)
        strip.fill((0, 0, 0))
        time.sleep(.25)
        i+=1
    
    strip.fill((255, 0, 0))
    time.sleep(2)
    strip.fill((0,0,0))
    

def app_on_light():
    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=1)
    
    strip.fill((0,0,50))
    
    
def pregame_light():
    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=.2)
    i = 0
    while i < 3:
        strip.fill((100, 50, 0))
        time.sleep(1)
        strip.fill((0,0,0))
        time.sleep(1)
        i+=1

def end_of_period_light():
    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=1)
    
    strip.fill((0, 100, 0))
    time.sleep(3)
    strip.fill((0,0,0))
    

def victory_light():
    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=1)
    
    i=0
    while i < 20:
        strip.fill((255,255,255))
        time.sleep(.05)
        strip.fill((0,0,0))
        i += 1
        time.sleep(.05)


def turn_off_lights():
    LED_COUNT = 144
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=0)
    strip.fill((0,0,0))
    
pregame_light()
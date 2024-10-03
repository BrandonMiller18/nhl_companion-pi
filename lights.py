#include all necessary packages to get LEDs to work with Raspberry Pi
import time
import json
import board
import neopixel


# Lighting effects to reuse
def strip_fill(led_count, strip, color):
    '''Fills strip one light at a time with a solid color'''
    for x in range(0, led_count):
        strip[x] = color
        time.sleep(0.01)
        
        
def strobe(strip, first_color, second_color):
    '''Strobe effect between two colors - use in a loop'''
    strip.fill(first_color)
    time.sleep(0.075)
    strip.fill(second_color)
    time.sleep(0.075)



def goal_light(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=1)
    
    i = 0
    
    strip.fill((255, 0, 0))
    time.sleep(2)
    strip.fill((0,0,0))
    time.sleep(1)
    
    for x in range(0, led_count):
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
    

def app_on_light(led_count, color):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=1)
    
    #takes in color arg for team primary color
    strip.fill(color)
    

def fut_light(led_count):
    
    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=.05)
    i = 0
    while i < 3:
        strip.fill((100, 50, 0))
        time.sleep(1)
        strip.fill((0,0,0))
        time.sleep(1)
        i+=1


def pregame_light(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=.2)
    i = 0
    while i < 3:
        strip.fill((100, 50, 0))
        time.sleep(1)
        strip.fill((0,0,0))
        time.sleep(1)
        i+=1

def period_light(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=1)
    
    strip.fill((0, 100, 0))
    time.sleep(3)
    strip.fill((0,0,0))
    

def victory_light(led_count, primary_color, secondary_color):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=1)
    
    strip_fill(led_count, strip, primary_color)
    strip_fill(led_count, strip, secondary_color)
    
    i=0
    while i < 10:
        strobe(strip, primary_color, secondary_color)
        
        i+=1
        
    strip_fill(led_count, strip, primary_color)
    strip_fill(led_count, strip, secondary_color)
    
    while i < 20:
        strobe(strip, primary_color, secondary_color)
        
        i+=1


def init_game_light(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=0.5)
    strip.fill((255, 0, 0))
    time.sleep(0.25)
    strip.fill((0, 0, 0))
    
    
def no_game_light(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=0.5)
    for i in range(255):
        strip.fill((i, 0, 0))
    
    time.sleep(0.25)
    strip.fill((0, 0, 0))


def turn_off_lights(led_count):

    #Initialise a strips variable, provide the GPIO Data Pin
    #utilised and the amount of LED Nodes on strip and brightness (0 to 1 value)
    strip = neopixel.NeoPixel(board.D18, led_count, brightness=0)
    strip.fill((0,0,0))
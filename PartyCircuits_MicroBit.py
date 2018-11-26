# ------------__ Hacking STEM – PartyCircuits_MicroBit.py – micro:bit __-----------
#  For use with the Party Circuits lesson plan for electricity basics
#  available from Microsoft Education Workshop at 
#  http://aka.ms/hackingSTEM
#
#  Overview: This project uses the Micro:Bit to control lights. It 
#  reads in commands from Excel via Serial and uses the commands to flash LEDs.
#
#  This project uses a BBC Micro:Bit microcontroller, information at:
#  https://microbit.org/
#
#  Comments, contributions, suggestions, bug reports, and feature
#  requests are welcome! For source code and bug reports see:
#  http://github.com/[TODO github path to Hacking STEM]
#
#  Copyright 2018, Jen Fox (AKA jenfoxbot)
#  Microsoft EDU Workshop - HackingSTEM
#  MIT License terms detailed in LICENSE.txt
# ===---------------------------------------------------------------===

#Import all of the Micro:Bit Library 
from microbit import *

testArray = [1,1,1,1]
commandArrayRaw = [0]*10
commandArray = [0]*10

# Setup & Config
display.off()  # Turns off LEDs to free up additional input pins
uart.init(baudrate=9600)  # Sets serial baud rate
DATA_RATE = 10 # Frequency of code looping
EOL = '\n' # End of Line Character

# These constants are the pins used on the micro:bit for the sensors 
ledPinArray = [pin0, pin1, pin2, pin3, pin4, pin10]
LED_PIN1 = pin0
LED_PIN2 = pin1
LED_PIN3 = pin2
LED_PIN4 = pin3
LED_PIN5 = pin4
LED_PIN6 = pin10 #10 is last analog input pin
ledPinArray2 = [LED_PIN1, LED_PIN2, LED_PIN3, LED_PIN4, LED_PIN5, LED_PIN6]

#Set constants
LED_TIME_OFF = 50

#Set variables for intensity and speed
LED_FLASH_SPEED = 10
LED_BRIGHT = 255
LED_MID_BRIGHT = 175
LED_DIM = 100
LED_FAST_SPEED = 250
LED_MED_SPEED = 500
LED_SLOW_SPEED = 1000

#Set variables for Excel Commands
#  LED status: 0 = off, 1 = on
ledStatusArray = [0]*6

def turnLedOn(pinNumber, brightness):
    if pinNumber == 0:
        pin0.write_analog(brightness)
    elif pinNumber == 1:
        pin1.write_analog(brightness)

def turnLedsOff():
    pin0.write_analog(0)
    pin1.write_analog(0)
    pin2.write_analog(0)

#Functions to translate the Excel Hex command sequence
#  Convert hex number into base 10 integer then into binary
def hexToBinary(hexNum):
    binNum = 0
    if hexNum != "":
        binNum = bin(int(hexNum,16)) 
    return binNum

#Split the binary string into command sequence
def splitBinary(binNum):
    binString = str(binNum)
    if len(binString) < 12:
       binString = '0b0{}'.format(binString[2:])
    intensityBin = binString[2:4]
    ledFlashSpeedBin = binString[4:6]
    ledStatusArrayBin = binString[6:]
    return intensityBin, ledFlashSpeedBin, ledStatusArrayBin

#Determine LED intensity
def ledIntensity(intensityBin):
    intensity = 0
    if intensityBin == "01":
        intensity = LED_DIM
    elif intensityBin == "10":
        intensity = LED_MID_BRIGHT
    elif intensityBin == "11":
        intensity = LED_BRIGHT
    return intensity

#Determine LED flash speed
def ledFlashSpeed(flashSpeedBin):
    flashSpeed = 0
    if flashSpeedBin == "01":
        flashSpeed = LED_SLOW_SPEED
    elif flashSpeedBin == "10":
        flashSpeed = LED_MED_SPEED
    elif flashSpeedBin == "11":
        flashSpeed = LED_FAST_SPEED 
    return flashSpeed

def turnOnLeds(intensity, ledStatus): #ledStatus is a string of length 6
    for i in ledStatus[:]:
        if ledStatus[i] == 1:
            if i == 0:
                pin0.write_analog(intensity)
            elif i == 1:
                 pin1.write_analog(intensity)  
            elif i == 2:
                pin2.write_analog(intensity)     
    ##THIS IS WHAT IS TURNING ON PIN1 -- NEED TO FIX #################################################
    for i in ledPinArray:
        turnLedOn(pin1,intensity)
       # print(ledStatusArray[i])
        #if commandArray[i] == 1:
         #   pin1.write_analog(ledBright) 

'''def LEDFlashSequence():
    #may need to rewrite flash sequence

def process_data(s):
    # processes the incoming data from Excel and sets it into appropriate variables
    global intensity, flash_speed, led_1, led_2, led_3, led_4, led_5, led_6
    loop = int(s[0])
    intensity = int(s[1],16)
    flash_speed = int(s[2],16)
    led_1 = int(s[3],16)
    led_2 = int(s[4],16)
    led_3 = int(s[5],16)
    led_4 = int(s[6],16)
    led_5 = int(s[7],16)
    led_6 = int(s[8],16)'''

#=============================================================================#
#---------------The Code Below Here is for Excel Communication----------------#
#=============================================================================#

# Array to hold the serial data
## CHANGE 8 TO A CONSTANT ####################################################################################
parsedData = [0] * 8

def getData():
    #   This function gets data from serial and builds it into a string
    global parsedData, builtString
    builtString = ""
    while uart.any() is True:
        byteIn = uart.read(1)
        if byteIn == b'\n':
            continue
        byteIn = str(byteIn)
        splitByte = byteIn.split("'")
        builtString += splitByte[1]
    parseData(builtString)
    return (parsedData)

def parseData(s):
    #   This function seperates the string into an array
    global parsedData
    if s != "":
        parsedData = s.split(",")

#=============================================================================#
#------------------------------Main Program Loop------------------------------#
#=============================================================================#
while (True):
    serial_in_data = getData() 
    isLoop = parsedData[0]
    commandArrayRaw = parsedData[1:]
    if commandArrayRaw != "":
        for i in range(0,len(commandArrayRaw[:])):
            commandNumber = i + 1 #store the command row in a variable
            commandArray[i] = hexToBinary(str(commandArrayRaw[i]))

            i, s, led = splitBinary(commandArray[i])
            intensity = ledIntensity(i)
            flashSpeed = ledFlashSpeed(s)

            turnOnLeds(LED_BRIGHT, testArray)
            sleep(flashSpeed)
            turnLedsOff()
            sleep(LED_TIME_OFF) 
    print(commandArray)
    #process_data(parsedData)
   
    if (serial_in_data[0] != "#pause"):
        #uart is the micro:bit command for serial
        uart.write('{}'.format(parsedData)+EOL)
        #uart.write('{},{},{},{},{},{}'.format(led_1, led_2, led_3, led_4, led_5, led_6)+EOL)
    sleep(DATA_RATE)
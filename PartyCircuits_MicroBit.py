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

testArray = [1,1,1,1] #For testing purposes only

# Setup & Config
display.off()  # Turns off LEDs to free up additional input pins
uart.init(baudrate=9600)  # Sets serial baud rate
DATA_RATE = 10 # Frequency of code looping
EOL = '\n' # End of Line Character

# These constants are the pins used on the micro:bit for the sensors 
ledPinList = [pin0, pin1, pin2, pin3, pin4, pin10]   #10 is last analog input pin

#Set constants
LED_TIME_OFF = 50

#Set variables for intensity and speed
LED_FLASH_SPEED = 10
LED_BRIGHT = 1023
LED_MID_BRIGHT = 1023*0.75
LED_DIM = 1023*0.5
LED_FAST_SPEED = 250
LED_MED_SPEED = 500
LED_SLOW_SPEED = 1000

#Set variables for Excel Commands
#  LED status: 0 = off, 1 = on
ledCommandList = [0]*6
commandArrayRaw = [0]*10
commandArray = [0]*10

got_data = False
play_infinitely = False
is_paused = False


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

#  Turn LEDs on based on Excel commands
def turnOnLeds(intensity, ledStatus): 
    for i in range(len(ledStatus)): 
        if ledStatus[i] == "1":
            ledPinList[i].write_analog(intensity)
 
#  Turn all LEDs off
def turnOffLeds():
    for i in range(0,len(ledPinList)):
        ledPinList[i].write_analog(0)

#Function to flash appropriate LEDs based on Excel commands
def ledFlashSequence(intensity, flashSpeed, ledCommandArray):
    turnOnLeds(intensity, ledCommandArray)
    sleep(flashSpeed)
    turnOffLeds()
    sleep(LED_TIME_OFF)


#=============================================================================#
#---------------The Code Below Here is for Excel Communication----------------#
#=============================================================================#

# Array to hold the serial data (8 = number of commands)
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
    return (builtString != "")

def parseData(s):
    #   This function seperates the string into an array
    global parsedData
    if s != "":
        parsedData = s.split(",")


def update_control_state():
    global got_data, is_paused, play_infinitely, commandArrayRaw
    got_data = getData()    
    if got_data:
        is_paused = parsedData[0] == "#pause"
        play_infinitely = parsedData[1] == "1" 
        commandArrayRaw = parsedData[2:] 


#=============================================================================#
#------------------------------Main Program Loop------------------------------#
#=============================================================================#

while (True):
    update_control_state()

    if got_data or play_infinitely:
        for command_index in range(len(commandArrayRaw)-1):
            # Leave for loop if we're paused
            if is_paused:
                break
            command = commandArrayRaw[command_index]    
            intensity, flashSpeed, ledCommandList = splitBinary(hexToBinary(command))
            intensity = ledIntensity(intensity)
            flashSpeed = ledFlashSpeed(flashSpeed)
            

            #uart is the micro:bit command for serial
            try:
                uart.write('{}{}'.format(command_index + 1, EOL))
            except:
                pass

            #LED Flash Sequence
            ledFlashSequence(intensity, flashSpeed, ledCommandList)
            sleep(DATA_RATE)            
        
            update_control_state()

        
 
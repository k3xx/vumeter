"""
Simple functionality for writing out bytes to a 8-bit DAC.

An Analog Devices AD557 was used with this code.
http://www.analog.com/static/imported-files/data_sheets/AD557.pdf
"""

from time import sleep
import RPi.GPIO as GPIO

DATA_PINS = [7, 8, 9, 10, 11, 21, 22, 23]
CE_PIN = 24    # Chip Enable
ALL_PINS = DATA_PINS + [CE_PIN]

# Create a bit mask for each data pin
def create_masks():
    value = 1
    while True:
        yield value
        value = value << 1

DATA_PINS_AND_MASKS = zip(DATA_PINS, create_masks())

def init():
    """Set all pins we're using as outputs and set the initial output to 0V.
    """
    GPIO.setmode(GPIO.BCM)

    for port in ALL_PINS:
        GPIO.setup(port, GPIO.OUT)

    # Set chip-select high so that we don't emit anything
    GPIO.output(CE_PIN, GPIO.HIGH)

    # Start with 0V
    write_byte(0)

def write_byte(value):
    """Write a new byte value to the data pins and toggle the Chip Enable pin
    so that the DAC latches the new value.
    """ 
    for port, mask in DATA_PINS_AND_MASKS:
        GPIO.output(port, GPIO.HIGH if value & mask else GPIO.LOW)
    
    # Toggle CE to make the DAC take the new value
    GPIO.output(CE_PIN, GPIO.LOW)
    sleep(3e-7)
    GPIO.output(CE_PIN, GPIO.HIGH)


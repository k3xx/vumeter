#!/usr/bin/python

"""
Send 8-bit PulseAudio peak sound samples to a digital-to-analog convertor
(which is intended to be connected to an analog VU meter).

"""

import os
import pwd

from peak_monitor import PeakMonitor

import sys
import PCF8591 as ADC


SINK_NAME = 'alsa_output.usb-Burr-Brown_from_TI_USB_Audio_DAC-00-DAC.analog-stereo'
METER_RATE = 16 # Hz, default 128

def main():
    ADC.setup(0x48) # Set up the GPIO pins used to talk to the DAC

    for sample in PeakMonitor(SINK_NAME, METER_RATE):
        # samples range from 0 to 127 so double them to get the full voltage
        # range of the DAC
#        print sample
        ADC.write(sample << 1)
     
if __name__ == '__main__':
    main()

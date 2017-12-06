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
#from interpolate import InterpolatedArray

### short table look up since VU output is not linear on 0 to 255 scale
#points = ((0, 0), (247, 180), (255, 255))
#table = InterpolatedArray(points)

SINK_NAME = 'alsa_output.usb-Burr-Brown_from_TI_USB_Audio_DAC-00-DAC.analog-stereo'
METER_RATE = 16 # Hz, default 128

def main():
    try:
        ADC.setup(0x48) # Set up the GPIO pins used to talk to the DAC
        monitor = PeakMonitor(SINK_NAME, METER_RATE)

        for sample in monitor:
            # samples range from 0 to 127 so double them to get the full voltage
            # range of the DAC ("<< 1")
#            sample = sample << 1
            sample = sample * 1.42  # reduce range for better VU scale
#            sample = table[sample] # ...using loopup table

#            print sample
            ADC.write(sample)

    except KeyboardInterrupt: #Ctrl+C pressed
        print
        print "Shutdown requested...exiting"

    monitor.flushqueue()
#    ADC.cleanup() # TODO
     
if __name__ == '__main__':
    main()

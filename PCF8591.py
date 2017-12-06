#!/usr/bin/env python
#
# copied from https://www.sunfounder.com/learn/sensor-kit-v2-0-for-raspberry-pi-b-plus/lesson-13-pcf8591-sensor-kit-v2-0-for-b-plus.html
#------------------------------------------------------
import smbus
import time

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

#check your PCF8591 address by type in 'sudo i2cdetect -y -1' in terminal.
def setup(Addr):
	global address
	address = Addr

def write(val):
	try:
		temp = val # move string value to temp
		temp = int(temp) # change string to integer
		# print temp to see on terminal else comment out
		bus.write_byte_data(address, 0x40, temp)
	except Exception, e:
		print "Error: Device address: 0x%2X" % address
		print e




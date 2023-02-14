#!/usr/bin/env python

from smbus2 import SMBus
import struct
import time
import sys

with SMBus(1) as bus:

    if len(sys.argv) != 3:
        print('incorrect arguments')
        exit(0)

    pwm_left = int(sys.argv[1])
    pwm_right = int(sys.argv[2])

    array_left = list(bytearray(struct.pack(">h", abs(pwm_left))))
    array_right = list(bytearray(struct.pack(">h", abs(pwm_right))))

    if(pwm_left < 0):
        array_left[0] |= 0x80

    if(pwm_right < 0):
        array_right[0] |= 0x80

    send_array = array_left + array_right

    while 1:
        # 0x01 is MOTOR_COMMAND
        try:
            bus.write_i2c_block_data(0x3C, 0x01, send_array)
        except IOError as e:
            print('IOError: %s' % e)
        time.sleep(0.025)

#!/usr/bin/env python

from smbus2 import SMBus
import struct
import time
import sys

with SMBus(1) as bus:

    if len(sys.argv) != 3:
        print('incorrect arguments')
        exit(0)

    servo_left = int(sys.argv[1])
    servo_right = int(sys.argv[2])

    array_left = list(bytearray(struct.pack('>h', servo_left)))
    array_right = list(bytearray(struct.pack('>h', servo_right)))

    #if(servo_left < 0):
    #    array_left[0] |= 0x80

    #if(servo_right < 0):
    #    array_right[0] |= 0x80

    send_array = array_left + array_right

    print(send_array)

    # 0x07 is SET_SERVO
    try:
        bus.write_i2c_block_data(0x3C, 0x07, send_array)
        print('servo commands sent');
    except IOError as e:
        print('IOError: %s' % e)

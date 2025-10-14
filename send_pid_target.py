#!/usr/bin/env python


DEVICE_ADDR = 0x3c

from smbus2 import SMBus
import struct
import time
import sys

with SMBus(1) as bus:


    if len(sys.argv) != 3:
        print('incorrect arguments')
        exit(0)

    target_left = float(sys.argv[1])
    target_right = float(sys.argv[2])

    target_left_array = bytearray(struct.pack("f", target_left))
    target_right_array = bytearray(struct.pack("f", target_right))

    send_array = target_left_array + target_right_array

    print(send_array)

    while 1:
        try:
            bus.write_i2c_block_data(DEVICE_ADDR, 0x02, send_array)
            time.sleep(0.05)  # notice 20hz
        except IOError as e:
            print('IOError: %s' % e)





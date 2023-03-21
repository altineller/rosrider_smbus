#!/usr/bin/env python

from smbus2 import SMBus
import struct
import time

with SMBus(1) as bus:

    linearX = 0.0
    angularZ = 1.0

    linear_x_array = list(bytearray(struct.pack("f", linearX)))
    angular_z_array = list(bytearray(struct.pack("f", angularZ)))

    send_array = linear_x_array + angular_z_array

    while 1:

        try:
            bus.write_i2c_block_data(0x3C, 0x03, send_array)
        except IOError as e:
            print('IOError: %s' % e)

        time.sleep(0.05)

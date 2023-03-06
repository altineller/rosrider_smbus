#!/usr/bin/env python

from smbus2 import SMBus
import struct
import time

with SMBus(1) as bus:

    posix_time = int(time.time())

    send_array = list(bytearray(struct.pack("i", posix_time)))

    # add checksum and or result reading
    bus.write_i2c_block_data(0x3C, 0x06, send_array)

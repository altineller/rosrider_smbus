#!/usr/bin/env python
from smbus2 import SMBus
import string
import struct
import sys
import crc8
import time


DEVICE_ADDR = 0x3c
SET_RTC = 0x06

with SMBus(1) as bus:

    while True:
        t = time.time()
        posix_time = int(t)
        sub = t - posix_time
        if sub < 0.0000005: break

    posix_time = 0
    data_array = bytearray(struct.pack("i", posix_time))

    '''
    for b in send_array:
        print(b)
    '''

    # packet structure
    # byte[] = { P1, P2, P3, P4 }

    try:
        bus.write_i2c_block_data(DEVICE_ADDR, SET_RTC, data_array)
        print(t)
    except IOError as e:
        print('IOError: %s' % e)

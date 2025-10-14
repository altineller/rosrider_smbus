#!/usr/bin/env python
from smbus2 import SMBus
import string
import struct
import sys
import crc8
import time


DEVICE_ADDR = 0x3c


'''
with SMBus(1) as bus:

    while True:
        t = time.time()
        posix_time = int(t)
        sub = t - posix_time
        if sub < 0.0000005: break

    send_array = list(bytearray(struct.pack("i", posix_time)))
    bus.write_i2c_block_data(DEVICE_ADDR, 0x06, send_array)

    print(t)

'''

with SMBus(1) as bus:

    setRTC = 0x06 # SET_RTC

    while True:
        t = time.time()
        posix_time = int(t)
        sub = t - posix_time
        if sub < 0.0000005: break

    send_array = bytearray(struct.pack("i", posix_time))

    hashVal = crc8.crc8()
    hashVal.update(send_array)
    write_checksum = int(hashVal.hexdigest(), 16)

    # last byte is checksum
    send_array.insert(len(send_array), write_checksum)

    #for b in send_array:
    #    print(b)

    '''
        packet structure
        byte[] = { 0, P1, P2, P3, P4, checksum }
    '''
    try:

        bus.write_i2c_block_data(DEVICE_ADDR, setRTC, send_array)
        print(t)
    except IOError as e:
        print('IOError: %s' % e)

#!/usr/bin/env python

from smbus2 import SMBus
import crc8

with SMBus(1) as bus:

    try:
        # read result
        result = bus.read_i2c_block_data(0x3C, 0xB0, 4)
        print('type: %d' % result[0])
        print('subtype: %d' % result[1])
        print('checksum: %d' % result[2])
        print('result: %d' % result[3])

    except IOError as e:
        print('IOError: %s' % e)

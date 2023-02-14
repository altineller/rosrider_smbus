#!/usr/bin/env python
from smbus2 import SMBus
import string
import struct
import sys
import crc8

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

with SMBus(1) as bus:

    if len(sys.argv) != 3:
        print('incorrect arguments: address intvalue')
        exit(0)

    if not sys.argv[1].startswith('0x') and is_hex(sys.argv[1]):
       print('invalid address')
       exit(0)

    address = int(sys.argv[1], 16)
    floatvalue = float(sys.argv[2])

    if address < 0x40 or address >= 0x80:
       print('invalid address for float')

    send_array = bytearray(struct.pack("f", floatvalue))

    hash = crc8.crc8()
    hash.update(send_array)
    write_checksum = int(hash.hexdigest(), 16)

    # first byte is address
    send_array.insert(0, address)

    # last byte is checksum
    send_array.insert(len(send_array), write_checksum)

    '''
        packet structure
        byte[] = { address, 1, 2, 3, 4, checksum }
        1, 2, 3, 4 = float value
    '''

    try:

        # 0x0B is EEPROM_WRITE_FLOAT
        bus.write_i2c_block_data(0x3C, 0x0B, send_array)
        result = bus.read_i2c_block_data(0x3C, 0xB0, 4)

        # check if correct result
        if result[0]==0 and result[1]==0x0B:
            # check that calculated and returned checksum is equal
            if write_checksum==result[2]:
                # check operation returned 0
                if result[3]==0:
                    print('SUCCESS')
                else:
                    print('WRITE FAIL: %d' % result[3])
            else:
                print('CHECKSUM FAIL' % result)
        else:
            print('ASSERT FAIL: %s' % result)

    except IOError as e:
        print('IOError: %s' % e)


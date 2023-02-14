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
    intvalue = int(sys.argv[2])

    if address >= 0x40:
       print('invalid address for int')

    send_array = bytearray(struct.pack("i", intvalue))

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
        1 least significant byte, 4 most significant byte
    '''

    try:

        # 0x0A is EEPROM_WRITE_INT
        bus.write_i2c_block_data(0x3C, 0x0A, send_array)
        result = bus.read_i2c_block_data(0x3C, 0xB0, 4)

        # check if correct result
        if result[0]==0 and result[1]==0x0A:
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




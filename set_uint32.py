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
        print('incorrect arguments: index uint32Value')
        print('PARAM_RTC_TRIM 0')
        exit()

    if not sys.argv[2].startswith('0x') and is_hex(sys.argv[2]):
        print('incorrect command')
        exit(0)

    paramAddr = 0x0C # EEPROM_WRITE_UINT32
    index = int(sys.argv[1])
    uint32Value = int(sys.argv[2], 16)

    uint32_array = bytearray([index])
    num_array = bytearray(struct.pack("i", uint32Value))

    send_array = bytearray(list(uint32_array) + list(num_array))

    hashVal = crc8.crc8()
    hashVal.update(send_array)
    write_checksum = int(hashVal.hexdigest(), 16)

    # last byte is checksum
    send_array.insert(len(send_array), write_checksum)

    #for b in send_array:
    #    print(b)

    '''
        packet structure
        byte[] = { index, 1, 2, 3, 4, checksum }
    '''
    try:

        bus.write_i2c_block_data(0x3C, paramAddr, send_array)
        result = bus.read_i2c_block_data(0x3C, 0xB0, 4) # 0xB0 is READ_RESULT address

        # check if correct result
        if result[0]==0x0 and result[1]==paramAddr:
            # check that calculated and returned checksum is equal
            if write_checksum==result[2]:
                # check operation returned 0
                if result[3]==0x0:
                    print('SUCCESS')
                elif result[3]==0x1:
                    print('UNCHANGED')
                else:
                    print('WRITE FAIL: %d' % result[3])
            else:
                print('CHECKSUM FAIL' % result)
        else:
            print('ASSERT FAIL: %s' % result)

    except IOError as e:
        print('IOError: %s' % e)
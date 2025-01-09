#!/usr/bin/env python
from smbus2 import SMBus
import string
import struct
import sys
import crc8


DEVICE_ADDR = 0x3c

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

with SMBus(1) as bus:

    if len(sys.argv) != 3:
        print('incorrect arguments: index uint16Value')
        print('PARAM_LEFT_FORWARD_DEADZONE 0')
        print('PARAM_LEFT_REVERSE_DEADZONE 1')
        print('PARAM_RIGHT_FORWARD_DEADZONE 2')
        print('PARAM_RIGHT_REVERSE_DEADZONE 3')
        exit(0)

    paramAddr = 0x0D # EEPROM_WRITE_INT16
    index = int(sys.argv[1])
    int16Value = int(sys.argv[2])

    int16_array = bytearray([index])
    num_array = bytearray(struct.pack("i", int16Value))

    send_array = bytearray(list(int16_array) + list(num_array))

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

        bus.write_i2c_block_data(DEVICE_ADDR, paramAddr, send_array)
        result = bus.read_i2c_block_data(DEVICE_ADDR, 0xB0, 4) # 0xB0 is READ_RESULT address

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

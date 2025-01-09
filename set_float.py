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
        print('incorrect arguments: index floatValue')
        print('PARAM_GEAR_RATIO 0')
        print('PARAM_WHEEL_DIA 1')
        print('PARAM_BASE_WIDTH 2')
        print('PARAM_MAIN_AMP_LIMIT 3')
        print('PARAM_BAT_VOLTS_HIGH 4')
        print('PARAM_BAT_VOLTS_LOW 5')
        print('PARAM_MAX_RPM 6')
        print('PARAM_LEFT_AMP_LIMIT 7')
        print('PARAM_RIGHT_AMP_LIMIT 8')
        print('PARAM_LEFT_KP 9')
        print('PARAM_LEFT_KI 10')
        print('PARAM_LEFT_KD 11')
        print('PARAM_RIGHT_KP 12')
        print('PARAM_RIGHT_KI 13')
        print('PARAM_RIGHT_KD 14')
        print('PARAM_GAIN 15')
        print('PARAM_TRIM 16')
        print('PARAM_MOTOR_CONSTANT 17')
        exit(0)

    paramAddr = 0x0F # EEPROM_WRITE_FLOAT
    index = int(sys.argv[1])
    floatvalue = float(sys.argv[2])

    num_array = bytearray(struct.pack("f", floatvalue))
    float_array = bytearray([index])
    send_array = bytearray(list(float_array) + list(num_array))

    hashVal = crc8.crc8()
    hashVal.update(send_array)
    write_checksum = int(hashVal.hexdigest(), 16)

    # last byte is checksum
    send_array.insert(len(send_array), write_checksum)

    for b in send_array:
        print(b)

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

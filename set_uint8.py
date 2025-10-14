#!/usr/bin/env python

from smbus2 import SMBus
import string
import struct
import sys
import crc8

DEVICE_ADDR = 0x3c

PARAM_WRITE = 0x01
PARAM_OVERRIDE = 0x02

I2C_WRITE_RESULT_SUCCESS = 0x00
I2C_WRITE_RESULT_UNCHANGED = 0x01
I2C_WRITE_RESULT_CHECKSUM = 0x03
I2C_WRITE_RESULT_OVERRIDE = 0xFF

RESULT_TYPE_WRITE_PARAM = 0x00
RESULT_TYPE_OVERRIDE_PARAM = 0x01

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

with SMBus(1) as bus:

    if len(sys.argv) < 3:
        print('incorrect arguments: index uint8Value')
        print('PARAM_CONFIG_FLAGS 0')
        print('PARAM_UPDATE_RATE 1')
        print('PARAM_PWM_DIV 2')
        print('PARAM_DRIVE_MODE 3')
        print('PARAM_MONITOR_RATE 4')
        print('PARAM_ALLOWED_SKIP 5')
        print('PARAM_I2C_ADDRESS 6')
        print('PARAM_OUTPUT_FILTER_TYPE 7')
        exit(0)

    override = len(sys.argv) > 3 and sys.argv[3] in ['override', '1', 'true']

    paramAddr = 0x0A # EEPROM_WRITE_UINT8
    index = int(sys.argv[1])

    if override:
        type = 0x02 # parameter override
        fp = int(sys.argv[4]) if len(sys.argv) > 4 else 0x00
    else:
        type = 0x01 # EEPROM Write
        fp = 0x00 # function pointer, not required

    uint8Value = int(sys.argv[2])

    uint16_array = bytearray([index, type, fp])
    num_array = bytearray(struct.pack("i", uint8Value))

    send_array = bytearray(list(uint16_array) + list(num_array))

    hashVal = crc8.crc8()
    hashVal.update(send_array)
    write_checksum = int(hashVal.hexdigest(), 16)

    # last byte is checksum
    send_array.insert(len(send_array), write_checksum)

    #for b in send_array:
    #    print(b)

    '''
        packet structure
        byte[] = { index, type, fp, 1, 2, 3, 4, checksum }
    '''
    try:

        bus.write_i2c_block_data(DEVICE_ADDR, paramAddr, send_array)
        result = bus.read_i2c_block_data(DEVICE_ADDR, 0xB0, 4) # 0xB0 is READ_RESULT address

        # check if correct result
        if (result[0]==RESULT_TYPE_WRITE_PARAM or result[0]==RESULT_TYPE_OVERRIDE_PARAM) and result[1]==paramAddr:

            # check that calculated and returned checksum is equal, indicating successful write
            if write_checksum == result[2]:

                # check operation returned 0
                if result[3] == I2C_WRITE_RESULT_SUCCESS:
                    print('SUCCESS')
                elif result[3] == I2C_WRITE_RESULT_UNCHANGED:
                    print('UNCHANGED')
                elif result[3] == I2C_WRITE_RESULT_OVERRIDE:
                    print('OVERRIDE');
                elif result[3] == I2C_WRITE_RESULT_CHECKSUM:
                    print('SENT CHECKSUM ERROR')
                else:
                    print('WRITE FAIL: %d' % result[3])
            else:
                print('CHECKSUM FAIL' % result)
        else:
            print('ASSERT FAIL: %s' % result)

    except IOError as e:
        print('IOError: %s' % e)

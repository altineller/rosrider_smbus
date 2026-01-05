#!/usr/bin/env python3

from smbus2 import SMBus
import struct
import sys
import crc8

DEVICE_ADDR = 0x3C

PARAM_WRITE = 0x01
PARAM_OVERRIDE = 0x02

I2C_WRITE_RESULT_SUCCESS = 0x00
I2C_WRITE_RESULT_UNCHANGED = 0x01
I2C_WRITE_RESULT_CHECKSUM = 0x03
I2C_WRITE_RESULT_OVERRIDE_FP_ERROR = 0xFE
I2C_WRITE_RESULT_OVERRIDE = 0xFF

RESULT_TYPE_WRITE_PARAM = 0x00
RESULT_TYPE_OVERRIDE_PARAM = 0x01

PARAMS_DESC = [
    "PARAM_LEFT_FORWARD_DEADZONE 0",
    "PARAM_LEFT_REVERSE_DEADZONE 1",
    "PARAM_RIGHT_FORWARD_DEADZONE 2",
    "PARAM_RIGHT_REVERSE_DEADZONE 3",
    "PARAM_CS_LEFT_OFFSET 4",
    "PARAM_CS_RIGHT_OFFSET 5"
]

def print_usage():
    print('Incorrect arguments: index int16Value [override [fp]]')
    for desc in PARAMS_DESC:
        print(desc)

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    try:
        index = int(sys.argv[1], 0)
        int16Value = int(sys.argv[2], 0)
    except ValueError:
        print("Error: index and int16Value must be integers.")
        sys.exit(2)

    override = len(sys.argv) > 3 and sys.argv[3].lower() in ['override', '1', 'true']
    paramAddr = 0x0D  # EEPROM_WRITE_INT16

    # TODO: when overriding, need to send window for execution.
    # TODO: depreciate override on python sets, or add fp index functionality

    if override:
        type_ = PARAM_OVERRIDE
        try:
            fp = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x00
        except ValueError:
            print("Error: fp must be an integer.")
            sys.exit(3)
    else:
        type_ = PARAM_WRITE
        fp = 0x00

    # Data packet: [index, type, fp, int16Value (4 bytes LE), checksum]
    packet = bytearray([index, type_, fp])
    packet.extend(struct.pack("<i", int16Value))  # Little-endian 4 bytes

    hash_obj = crc8.crc8()
    hash_obj.update(packet)
    checksum = int(hash_obj.hexdigest(), 16)
    packet.append(checksum)

    try:
        with SMBus(1) as bus:
            bus.write_i2c_block_data(DEVICE_ADDR, paramAddr, list(packet))
            result = bus.read_i2c_block_data(DEVICE_ADDR, 0xB0, 4)

            # Validate result
            if (result[0] in [RESULT_TYPE_WRITE_PARAM, RESULT_TYPE_OVERRIDE_PARAM]) and result[1] == paramAddr:
                if checksum == result[2]:
                    if result[3] == I2C_WRITE_RESULT_SUCCESS:
                        print('SUCCESS')
                    elif result[3] == I2C_WRITE_RESULT_UNCHANGED:
                        print('UNCHANGED')
                    elif result[3] == I2C_WRITE_RESULT_OVERRIDE:
                        print('OVERRIDE')
                    elif result[3] == I2C_WRITE_RESULT_CHECKSUM:
                        print('SENT CHECKSUM ERROR')
                    elif result[3] == I2C_WRITE_RESULT_CHECKSUM:
                        print('SENT CHECKSUM ERROR')
                    else:
                        print(f'WRITE FAIL: {result[3]}')
                else:
                    print(f'CHECKSUM FAIL: sent {checksum}, got {result[2]}')
            else:
                print(f'ASSERT FAIL: {result}')
    except IOError as e:
        print(f'IOError: {e}')
    except Exception as ex:
        print(f'Unexpected error: {ex}')

if __name__ == "__main__":
    main()

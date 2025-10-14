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
I2C_WRITE_RESULT_OVERRIDE = 0xFF

RESULT_TYPE_WRITE_PARAM = 0x00
RESULT_TYPE_OVERRIDE_PARAM = 0x01

PARAMS_DESC = [
    "PARAM_CONFIG_FLAGS 0",
    "PARAM_UPDATE_RATE 1",
    "PARAM_PWM_DIV 2",
    "PARAM_DRIVE_MODE 3",
    "PARAM_MONITOR_RATE 4",
    "PARAM_ALLOWED_SKIP 5",
    "PARAM_I2C_ADDRESS 6",
    "PARAM_OUTPUT_FILTER_TYPE 7"
]

def print_usage():
    print('Incorrect arguments: index uint8Value [override [fp]]')
    for desc in PARAMS_DESC:
        print(desc)

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    # Input flag parsing (kept mostly as original for minimal change)
    try:
        index = int(sys.argv[1], 0)
        uint8Value = int(sys.argv[2], 0)
    except ValueError:
        print("Error: index and uint8Value must be integers.")
        sys.exit(2)

    override = len(sys.argv) > 3 and sys.argv[3].lower() in ['override', '1', 'true']
    paramAddr = 0x0A  # EEPROM_WRITE_UINT8

    if override:
        type_op = PARAM_OVERRIDE
        try:
            fp = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x00
        except ValueError:
            print("Error: fp must be an integer.")
            sys.exit(3)
    else:
        type_op = PARAM_WRITE
        fp = 0x00

    # Data packet
    packet = bytearray([index, type_op, fp])
    packet.extend(struct.pack("<i", uint8Value))  # Little-endian 4 bytes

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
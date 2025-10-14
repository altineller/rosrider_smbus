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
    "PARAM_GEAR_RATIO 0",
    "PARAM_WHEEL_DIA 1",
    "PARAM_BASE_WIDTH 2",
    "PARAM_MAIN_AMP_LIMIT 3",
    "PARAM_BAT_VOLTS_HIGH 4",
    "PARAM_BAT_VOLTS_LOW 5",
    "PARAM_MAX_RPM 6",
    "PARAM_LEFT_AMP_LIMIT 7",
    "PARAM_RIGHT_AMP_LIMIT 8",
    "PARAM_LEFT_KP 9",
    "PARAM_LEFT_KI 10",
    "PARAM_LEFT_KD 11",
    "PARAM_RIGHT_KP 12",
    "PARAM_RIGHT_KI 13",
    "PARAM_RIGHT_KD 14",
    "PARAM_GAIN 15",
    "PARAM_TRIM 16",
    "PARAM_MOTOR_CONSTANT 17"
]

def print_usage():
    print('Incorrect arguments: index floatValue [override [fp]]')
    for desc in PARAMS_DESC:
        print(desc)

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    try:
        index = int(sys.argv[1], 0)
        floatValue = float(sys.argv[2])
    except ValueError:
        print("Error: index must be integer and floatValue must be a float.")
        sys.exit(2)

    override = len(sys.argv) > 3 and sys.argv[3].lower() in ['override', '1', 'true']
    paramAddr = 0x0F  # EEPROM_WRITE_FLOAT

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

    # Data packet: [index, type, fp, floatValue (4 bytes LE float), checksum]
    packet = bytearray([index, type_op, fp])
    packet.extend(struct.pack("<f", floatValue))  # Little-endian float

    hash_obj = crc8.crc8()
    hash_obj.update(packet)
    checksum = int(hash_obj.hexdigest(), 16)
    packet.append(checksum)

    for b in packet:
        print(b)

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
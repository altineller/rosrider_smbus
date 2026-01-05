#!/usr/bin/env python3

from smbus2 import SMBus
import struct
import sys
import crc8

DEVICE_ADDR = 0x3C

UPDATE_SUCCESS = 0x00
UPDATE_UNCHANGED = 0x10
UPDATE_WR_ERROR = 0x21
UPDATE_CHECKSUM = 0x22
UPDATE_DENIED = 0x30
UPDATE_FP_ERROR = 0x40
UPDATE_REBOOT = 0x80

EEPROM_WRITE_FLOAT = 0x0F

PARAMS_DESC = [
    'GEAR_RATIO 0',
    'WHEEL_DIA 1',
    'BASE_WIDTH 2',
    'MAIN_AMP_LIMIT 3',
    'BAT_VOLTS_HIGH 4',
    'BAT_VOLTS_LOW 5',
    'MAX_RPM 6',
    'LEFT_AMP_LIMIT 7',
    'RIGHT_AMP_LIMIT 8',
    'LEFT_KP 9',
    'LEFT_KI 10',
    'LEFT_KD 11',
    'RIGHT_KP 12',
    'RIGHT_KI 13',
    'RIGHT_KD 14',
    'TRIM_GAIN 15',
    'TRIM_CONSTANT 16',
    'TRIM_MOTOR_K 17',
    'TANH_DIV 18',
    'SIGM_DIV 19',
    'CURRENT_KP 20',
    'CURRENT_KI 21',
    'CURRENT_MULTIPLIER_LEFT 22',
    'CURRENT_MULTIPLIER_RIGHT 23',
    'KB 24',
    'R_ARM 25',
    'K_FF_VEL 26',
    'K_FF_ACCEL 27',
    'STATIC_KICK 28',
    'COULOMB_RUN 29',
    'STRIBECK_WIDTH 30',
    'VISCOUS_FRICTION 31',
    'VISCOUS_FRICTION_LIMIT 32',
    'EB_FF_LIMIT 33',
    'LEFT_KT 34',
    'LEFT_KT_W 35',
    'RIGHT_KT 36',
    'RIGHT_KT_W 37',
    'CROSS_KP 38',
    'CROSS_K_LEFT 39',
    'CROSS_K_RIGHT 40',
    'SCV_OMEGA_THRESHOLD 41',
    'SCV_LATCH_THRESHOLD 42',
    'CURRENT_OMEGA_K_LEFT 43',
    'CURRENT_OMEGA_K_RIGHT 44'
]

def print_usage():
    print('Incorrect arguments: INDEX float')
    for desc in PARAMS_DESC:
        print(desc)

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    try:
        FP_IDX = int(sys.argv[1], 0)
        floatVALUE = float(sys.argv[2])
    except ValueError:
        print('Error: INDEX must be INTEGER and floatVALUE must be FLOAT')
        sys.exit(2)

    # Data packet: [FP_IDX, 0, 0, floatVALUE, CHECKSUM]
    packet = bytearray([FP_IDX, 0, 0])
    packet.extend(struct.pack('<f', floatVALUE))  # Little-endian float

    hash_obj = crc8.crc8()
    hash_obj.update(packet)
    CALCULATED_CHECKSUM = int(hash_obj.hexdigest(), 16)
    packet.append(CALCULATED_CHECKSUM)

    #for b in packet:
    #    print(b)

    try:
        with SMBus(1) as bus:

            # write to i2c bus
            bus.write_i2c_block_data(DEVICE_ADDR, EEPROM_WRITE_FLOAT, list(packet))

	    # read result
            result = bus.read_i2c_block_data(DEVICE_ADDR, 0xB0, 4)

            if result[0] == EEPROM_WRITE_FLOAT :
                if CALCULATED_CHECKSUM == result[2] :
                    write_result = result[3]
                    print(write_result)
                else:
                    print(f'CALCULATED CHECKSUM FAIL: SENT {CALCULATED_CHECKSUM}, RECV {result[2]}')
            else:
                print(f'ASSERT FAIL: {result}')

    except IOError as e:
        print(f'IOError: {e}')
    except Exception as ex:
        print(f'Unexpected error: {ex}')

if __name__ == '__main__':
    main()

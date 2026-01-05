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

EEPROM_WRITE_BOOL = 0x0E

PARAMS_DESC = [
   'AUTO_SYNC 0',
   'ADC_SYNC 1',
   'CASCADED 2',
   'AUTO_BIAS 3',
   'ADC_MULTIPHASE 4',
   'ADC_BIPHASE 5',
   'OUTER_FEEDFORWARD 6',
   'OUTER_SCV 7',
   'VOLTAGE_FILTER 8',
   'AUTO_BRAKE 9',
   'BEMF_USE_OMEGA_FILTER 10',
   'CROSS_COUPLED_CONTROL 11',
   'PID_USE_OMEGA_FILTER 12',
   'SCV_USE_OMEGA_FILTER 13',
   'CURRENT_OMEGA_FILTER 14'
]

def print_usage():
    print('Incorrect arguments: INDEX bool')
    for desc in PARAMS_DESC:
        print(desc)

def t_or_f(arg):
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
        return True
    elif 'FALSE'.startswith(ua):
        return False
    else:
        raise ValueError(f"Unknown boolVALUE {arg}")

def main():

    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    try:
        FP_IDX = int(sys.argv[1], 0)
        boolVALUE = t_or_f(sys.argv[2])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)

    intVALUE = 1 if boolVALUE else 0

    # Data packet: [FP_IDX, type, fp, intVALUE, CHECKSUM]
    packet = bytearray([FP_IDX, 0, 0])
    packet.extend(struct.pack("<i", intVALUE))  # little-endian 4 int

    hash_obj = crc8.crc8()
    hash_obj.update(packet)
    CALCULATED_CHECKSUM = int(hash_obj.hexdigest(), 16)
    packet.append(CALCULATED_CHECKSUM)

    #for b in packet:
    #    print(b)

    try:
        with SMBus(1) as bus:

            # write to i2c bus
            bus.write_i2c_block_data(DEVICE_ADDR, EEPROM_WRITE_BOOL, list(packet))

            # read results
            result = bus.read_i2c_block_data(DEVICE_ADDR, 0xB0, 4)

            # result: { type, reboot, crc, result }

            if result[0] == EEPROM_WRITE_BOOL :
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

if __name__ == "__main__":
    main()

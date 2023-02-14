#!/usr/bin/env python

from smbus2 import SMBus
import struct
import sys

with SMBus(1) as bus:

    if len(sys.argv) != 5:
        print('incorrect arguments')
        print('usage: set_pid_k.py kP kI kD 0|1')
        exit(0)

    kP = float(sys.argv[1])
    kI = float(sys.argv[2])
    kD = float(sys.argv[3])

    if (kP < 0.0) or (kI < 0.0) or (kD < 0.0):
        print('can not accept negative coefficients')
        exit(0)

    i = int(sys.argv[4])

    if i not in [0,1]:
        print('pid index out of bound')
        exit(0)

    p_array = bytearray(struct.pack("f", kP))
    i_array = bytearray(struct.pack("f", kI))
    d_array = bytearray(struct.pack("f", kD))

    send_array = p_array + i_array + d_array

    # PID_TUNE_LEFT 0x08
    # PID_TUNE_RIGHT 0x09
    try:
        if i==0:
            bus.write_i2c_block_data(0x3C, 0x08, send_array)
        elif i==1:
            bus.write_i2c_block_data(0x3C, 0x09, send_array)
    except IOError as e:
        print('IOError: %s' % e)

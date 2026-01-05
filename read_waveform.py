#!/usr/bin/env python

from smbus2 import SMBus
import crc8

WAVEFORM_BUFFER_SIZE = 32
DEVICE_ADDR = 0x3c

with SMBus(1) as bus:

    try:

        left_waveform0 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC0, WAVEFORM_BUFFER_SIZE)
        left_waveform1 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC1, WAVEFORM_BUFFER_SIZE)
        left_waveform2 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC2, WAVEFORM_BUFFER_SIZE)
        left_waveform3 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC3, WAVEFORM_BUFFER_SIZE)
        left_waveform4 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC4, WAVEFORM_BUFFER_SIZE)
        left_waveform5 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC5, WAVEFORM_BUFFER_SIZE)
        left_waveform6 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC6, WAVEFORM_BUFFER_SIZE)
        left_waveform7 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC7, WAVEFORM_BUFFER_SIZE)

        print(left_waveform0)
        print(left_waveform1)
        print(left_waveform2)
        print(left_waveform3)
        print(left_waveform4)
        print(left_waveform5)
        print(left_waveform6)
        print(left_waveform7)

        right_waveform0 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD0, WAVEFORM_BUFFER_SIZE)
        right_waveform1 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD1, WAVEFORM_BUFFER_SIZE)
        right_waveform2 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD2, WAVEFORM_BUFFER_SIZE)
        right_waveform3 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD3, WAVEFORM_BUFFER_SIZE)
        right_waveform4 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD4, WAVEFORM_BUFFER_SIZE)
        right_waveform5 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD5, WAVEFORM_BUFFER_SIZE)
        right_waveform6 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD6, WAVEFORM_BUFFER_SIZE)
        right_waveform7 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD7, WAVEFORM_BUFFER_SIZE)

        print(right_waveform0)
        print(right_waveform1)
        print(right_waveform2)
        print(right_waveform3)
        print(right_waveform4)
        print(right_waveform5)
        print(right_waveform6)
        print(right_waveform7)

        interrupt_marks = bus.read_i2c_block_data(DEVICE_ADDR, 0xDF, WAVEFORM_BUFFER_SIZE)
        print(interrupt_marks)

    except IOError as e:
        print('IOError: %s' % e)

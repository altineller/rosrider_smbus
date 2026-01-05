#!/usr/bin/env python

# TODO: make this even a c program later on
# TODO: read_state and show status at the bottom

import crc8
import time
import os

import argparse

import plotille
from smbus2 import SMBus

WAVEFORM_BUFFER_SIZE = 32
STATUS_BUFFER_SIZE = 32
DEVICE_ADDR = 0x3c

# initialize waveform variables to None
waveform0 = None
waveform1 = None
waveform2 = None
waveform3 = None
waveform4 = None
waveform5 = None
waveform6 = None
waveform7 = None

flag_A = False
flag_B = False
flag_CNT = False

parser = argparse.ArgumentParser(description='Plot waveform data from I2C device')

parser.add_argument('--CH0', action='store_true', help='Display CH0');
parser.add_argument('--CH1', action='store_true', help='Display CH1');

parser.add_argument('--CNT', action='store_true', help='Display LOAD/CNT')

args = parser.parse_args()

flag_A = args.CH0
flag_B = args.CH1
flag_CNT = args.CNT

try:

    counter = 0
    fig = plotille.Figure()

    while True:

        fig.clear()

        with SMBus(1) as bus:
            try:
                # 0x04 is sys_ctl address
                bus.write_i2c_block_data(DEVICE_ADDR, 0x04, [0,0,0,0xE0])
            except IOError as e:
                print('IOError sending SYSCTL request to trigger ADC: %s' % e)

            try:
    	        with SMBus(1) as bus:
                    # Read 32 bytes from registers 0xC0 through 0xC7
                    left_waveform0 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC0, WAVEFORM_BUFFER_SIZE)
                    left_waveform1 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC1, WAVEFORM_BUFFER_SIZE)
                    left_waveform2 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC2, WAVEFORM_BUFFER_SIZE)
                    left_waveform3 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC3, WAVEFORM_BUFFER_SIZE)
                    left_waveform4 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC4, WAVEFORM_BUFFER_SIZE)
                    left_waveform5 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC5, WAVEFORM_BUFFER_SIZE)
                    left_waveform6 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC6, WAVEFORM_BUFFER_SIZE)
                    left_waveform7 = bus.read_i2c_block_data(DEVICE_ADDR, 0xC7, WAVEFORM_BUFFER_SIZE)
            except IOError as e:
                print('-' * 60)
                print(f'FATAL I2C ERROR: could not read data from device 0x{DEVICE_ADDR:02x} on bus 1.')
                print(f'details: {e}')
                print('execution halted. check device connection, address, and bus permissions.')
                print('-' * 60)
                exit(1) # exit immediately if I2C read fails
            try:
                with SMBus(1) as bus:
                    # Read 32 bytes from registers 0xD0 through 0xD7
                    right_waveform0 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD0, WAVEFORM_BUFFER_SIZE)
                    right_waveform1 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD1, WAVEFORM_BUFFER_SIZE)
                    right_waveform2 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD2, WAVEFORM_BUFFER_SIZE)
                    right_waveform3 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD3, WAVEFORM_BUFFER_SIZE)
                    right_waveform4 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD4, WAVEFORM_BUFFER_SIZE)
                    right_waveform5 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD5, WAVEFORM_BUFFER_SIZE)
                    right_waveform6 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD6, WAVEFORM_BUFFER_SIZE)
                    right_waveform7 = bus.read_i2c_block_data(DEVICE_ADDR, 0xD7, WAVEFORM_BUFFER_SIZE)
            except IOError as e:
                print('-' * 60)
                print(f'FATAL I2C ERROR: could not read data from device 0x{DEVICE_ADDR:02x} on bus 1.')
                print(f'details: {e}')
                print('execution halted. check device connection, address, and bus permissions.')
                print('-' * 60)
                exit(1) # exit immediately if I2C read fails

            try:
                with SMBus(1) as bus:

                    # read 32 bytes from register 0xDD
                    pwm_a_state = bus.read_i2c_block_data(DEVICE_ADDR, 0xDD, WAVEFORM_BUFFER_SIZE)
                    pwm_a_state_indices = []

                    # iterate through each of the 32 packed bytes
                    for byte_index, byte_value in enumerate(pwm_a_state):
                       # iterate through the 8 bits of the current byte (bit_position is 0 to 7)
                       for bit_position in range(8):
                           if byte_value & (1 << bit_position):
                               global_index = (byte_index * 8) + bit_position + 1
                               pwm_a_state_indices.append(global_index)

                    # read 32 bytes from register 0xDF
                    pwm_b_state = bus.read_i2c_block_data(DEVICE_ADDR, 0xDE, WAVEFORM_BUFFER_SIZE)
                    pwm_b_state_indices = []

                    # iterate through each of the 32 packed bytes
                    for byte_index, byte_value in enumerate(pwm_b_state):
                       # iterate through the 8 bits of the current byte (bit_position is 0 to 7)
                       for bit_position in range(8):
                           if byte_value & (1 << bit_position):
                               global_index = (byte_index * 8) + bit_position + 1
                               pwm_b_state_indices.append(global_index)

                    # read 32 bytes from register 0xDD
                    pwm_cnt_state = bus.read_i2c_block_data(DEVICE_ADDR, 0xDF, WAVEFORM_BUFFER_SIZE)
                    pwm_cnt_state_indices = []

                    # iterate through each of the 32 packed bytes
                    for byte_index, byte_value in enumerate(pwm_cnt_state):
                       # iterate through the 8 bits of the current byte (bit_position is 0 to 7)
                       for bit_position in range(8):
                           if byte_value & (1 << bit_position):
                               global_index = (byte_index * 8) + bit_position + 1
                               pwm_cnt_state_indices.append(global_index)

            except IOError as e:
                print('-' * 60)
                print(f'FATAL I2C ERROR: could not read data from device 0x{DEVICE_ADDR:02x} on bus 1.')
                print(f'details: {e}')
                print('execution halted. check device connection, address, and bus permissions.')
                print('-' * 60)
                exit(1) # exit immediately if I2C read fails

            try:
                with SMBus(1) as bus:

                    # TODO: this is static for 20hz, 48ppr, 65:1
                    ROUNDS_PER_MINUTE = (60.0 / (1.0 / 20)) / (48 * 65)

                    # read status
                    status = bus.read_i2c_block_data(DEVICE_ADDR, 0xA0, STATUS_BUFFER_SIZE)
                    rpm_left = ( status[20] << 8 | status[21] ) * ROUNDS_PER_MINUTE
                    rpm_right = ( status[22] << 8 | status[23] ) * ROUNDS_PER_MINUTE

            except IOError as e:
                print('-' * 60)
                print(f'FATAL I2C ERROR: could not read data from device 0x{DEVICE_ADDR:02x} on bus 1.')
                print(f'details: {e}')
                print('execution halted. check device connection, address, and bus permissions.')
                print('-' * 60)
                exit(1) # exit immediately if I2C read fails

        # combine each block
        waveform_left = [left_waveform0, left_waveform1, left_waveform2, left_waveform3, left_waveform4, left_waveform5, left_waveform6, left_waveform7]
        waveform_right = [right_waveform0, right_waveform1, right_waveform2, right_waveform3, right_waveform4, right_waveform5, right_waveform6, right_waveform7]

        if all(w is not None for w in waveform_left):

            # combine all 8 waveform buffers into one continuous list
            left_waveforms = []
            for w in waveform_left:
                left_waveforms.extend(w)
            right_waveforms = []
            for w in waveform_right:
                right_waveforms.extend(w)

            x_data = list(range(len(left_waveforms)))

            # fig = plotille.Figure()

            fig.width = 128        # width of the plot in characters
            fig.height = 32       # height of the plot in lines
            fig.x_label = 'time'
            fig.y_label = 'current'
            fig.set_x_limits(0, 256)
            fig.set_y_limits(0, 256)
            fig.color_mode = 'rgb'
            fig.origin = False
            fig.interp = None
            # fig.interp='linear'

            # add the waveform data to the figure
            left_y_data = [int(val) for val in left_waveforms]
            right_y_data = [int(val) for val in right_waveforms]

            print(rpm_left)

            left_rpm_data = [rpm_left] * 256
            right_rpm_data = [rpm_right] * 256

            MARK_HEIGHT = 256
            mark_a_data = [-2] * 256
            mark_b_data = [-2] * 256
            mark_cnt_data = [-2] * 256

            for pwm_a_state in pwm_a_state_indices:
                mark_a_data[pwm_a_state - 1] = MARK_HEIGHT

            for pwm_b_state in pwm_b_state_indices:
                mark_b_data[pwm_b_state - 1] = MARK_HEIGHT

            for pwm_cnt_state in pwm_cnt_state_indices:
                mark_cnt_data[pwm_cnt_state - 1] = MARK_HEIGHT

            if flag_A:
                fig.plot(x_data, left_y_data, label="left_cs", lc='ff0000')
                fig.plot(x_data, mark_a_data, label="pwm_a", lc='880000')

            if flag_B:
                fig.plot(x_data, right_y_data, label="right_cs", lc='0000ff')
                fig.plot(x_data, mark_b_data, label="pwm_b", lc='000088')

            if flag_CNT:
                fig.plot(x_data, mark_cnt_data, label="cnt", lc='008800')


            fig.plot(x_data, left_rpm_data, label="left_rpm", lc='444400')

            os.system('clear')
            print(fig.show(legend=False))

        else:
            # this block is now mostly redundant but kept as a final safety check
           print("FATAL ERROR: Waveform data was unexpectedly empty after I2C read.")
           exit(1)

        counter += 1
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nPlotting stopped by user.")

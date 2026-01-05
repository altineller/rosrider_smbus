#!/usr/bin/env python

from smbus2 import SMBus
import struct
import time
import sys
import crc8
import math

# --- CONFIGURATION ---
DEVICE_ADDR = 0x3c
BUS_NUM = 1
STATUS_BUFFER_SIZE = 32

# MOTOR PHYSICAL CONSTANTS
GEAR_RATIO = 65.0
ENCODER_PPR = 48
MOTOR_RESISTANCE_OHM = 2.0

# PWM STEPPING PARAMETERS
PWM_START = 0
PWM_END = 192
PWM_STEP = 16
PWM_SCALE = 256.0
TIME_HOLD_SECONDS = 5.0
AVERAGE_COUNT = 5
LOG_FILENAME = 'pwm_profile_log_dual_kt.csv' # Updated filename
MCU_OFFSET_CURRENT_A = 0.050

# COMMUNICATION TIMING
COMMAND_RATE_HZ = 20
COMMAND_PERIOD_SEC = 1.0 / COMMAND_RATE_HZ
FIRMWARE_VELOCITY_RATE_HZ = 20.0

# --- STATUS PACKET CONSTANTS ---
BUS_VOLTAGE_DIVIDER = 1000.0
CURRENT_CONVERSION_UNSCALER = 6.6 / 32767.0
BUS_CURRENT_DIVIDER = 10000.0
ROUNDS_PER_MINUTE_FACTOR = (60.0 * FIRMWARE_VELOCITY_RATE_HZ) / (ENCODER_PPR * GEAR_RATIO)

# --- UTILITY FUNCTIONS ---
def unsignedToSigned(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, 'little', signed=False), 'little', signed=True)

def send_pwm_command(bus, pwm_left, pwm_right):
    """Encodes and sends PWM command over I2C."""
    abs_pwm_left = abs(pwm_left)
    array_left = list(bytearray(struct.pack(">h", abs_pwm_left)))
    if(pwm_left < 0): array_left[0] |= 0x80

    abs_pwm_right = abs(pwm_right)
    array_right = list(bytearray(struct.pack(">h", abs_pwm_right)))
    if(pwm_right < 0): array_right[0] |= 0x80

    send_array = array_left + array_right
    try:
        bus.write_i2c_block_data(DEVICE_ADDR, 0x01, send_array)
    except IOError as e:
        pass

def read_status_packet(bus):
    """Reads and parses a single status packet."""
    try:
        status = bus.read_i2c_block_data(DEVICE_ADDR, 0xA0, STATUS_BUFFER_SIZE)
    except IOError:
        return None, "IOError reading status"

    hash_obj = crc8.crc8()
    hash_obj.update(bytearray(status[0:29]))
    calculated_checksum = int(hash_obj.hexdigest(), 16)
    packet_checksum = status[31]

    if calculated_checksum != packet_checksum:
        return None, "Checksum Mismatch"

    # --- Data Extraction ---
    bus_current_raw = status[8] << 8 | status[9]
    bus_current_total_amps = bus_current_raw / BUS_CURRENT_DIVIDER

    bus_voltage_raw = status[10] << 8 | status[11]
    bus_voltage_volts = bus_voltage_raw / BUS_VOLTAGE_DIVIDER

    cs_right_raw = status[14] << 8 | status[15]
    cs_right_amps = cs_right_raw * CURRENT_CONVERSION_UNSCALER

    rpm_right_raw = status[22] << 8 | status[23]
    enc_dir_right = ((status[24] & 0xF0) >> 4) - 1

    rpm_right_signed = rpm_right_raw * ROUNDS_PER_MINUTE_FACTOR * enc_dir_right
    pwm_right_read = unsignedToSigned(status[16] << 8 | status[17], 2)

    # --- TRUE DC MOTOR CURRENT CALCULATION ---
    i_true_dc_motor = max(0.0, bus_current_total_amps - MCU_OFFSET_CURRENT_A)

    return {
        'pwm_command_read': pwm_right_read,
        'rpm_right': rpm_right_signed,
        'bus_voltage': bus_voltage_volts,
        'cs_right_amps': cs_right_amps,
        'i_true_dc_motor': i_true_dc_motor 
    }, None

# --- MAIN PROFILER LOGIC ---

with SMBus(BUS_NUM) as bus:

    # Open log file and write header
    with open(LOG_FILENAME, 'w') as f:
        # Header with BOTH Kt values
        f.write('PWM_Command_Sent,RPM_Output,Bus_Voltage_V,CS_right_A,I_Bus_Motor_A,V_App_V,Kt_SI_Nm_A,Kt_ADC_Nm_A\n')

        print(f"--- PWM Ramp Profiler Started (Gear Ratio: {GEAR_RATIO}:1) ---")
        print(f"Logging to {LOG_FILENAME}")
        print("PWM | RPM | I_True | I_ADC | Kt(SI) | Kt(ADC)")

        # Ramp loop
        for pwm_cmd in range(PWM_START, PWM_END + PWM_STEP, PWM_STEP):

            # 1. INITIAL COMMAND AND START TIME
            print(f"Setting PWM: {pwm_cmd}...")

            # 2. ROBUST STABILIZATION LOOP
            num_commands = int(TIME_HOLD_SECONDS / COMMAND_PERIOD_SEC)
            start_time = time.time()

            for i in range(num_commands):
                send_pwm_command(bus, 0, pwm_cmd)
                time_to_wait = start_time + (i + 1) * COMMAND_PERIOD_SEC - time.time()
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

            time_to_wait_final = start_time + TIME_HOLD_SECONDS - time.time()
            if time_to_wait_final > 0:
                 time.sleep(time_to_wait_final)

            # 3. MEASUREMENT PHASE
            sum_rpm = 0.0
            sum_voltage = 0.0
            sum_cs_right = 0.0
            sum_i_true_dc_motor = 0.0
            valid_reads = 0

            for _ in range(AVERAGE_COUNT):
                measurement_start_time = time.time()

                send_pwm_command(bus, 0, pwm_cmd)
                time.sleep(0.01) 

                data, error = read_status_packet(bus)
                if data and error is None:
                    sum_rpm += data['rpm_right']
                    sum_voltage += data['bus_voltage']
                    sum_cs_right += data['cs_right_amps']
                    sum_i_true_dc_motor += data['i_true_dc_motor']
                    valid_reads += 1

                time_to_wait_meas = measurement_start_time + COMMAND_PERIOD_SEC - time.time()
                if time_to_wait_meas > 0:
                    time.sleep(time_to_wait_meas)

            if valid_reads > 0:
                # Calculate Averages
                avg_rpm_output = sum_rpm / valid_reads
                avg_voltage = sum_voltage / valid_reads
                avg_cs_right = sum_cs_right / valid_reads
                avg_i_true_dc_motor = sum_i_true_dc_motor / valid_reads 

                # --- DUAL Kt CALCULATION ---

                # Common Physics
                v_app = avg_voltage * (float(pwm_cmd) / PWM_SCALE)
                rpm_motor = avg_rpm_output * GEAR_RATIO
                omega_motor = rpm_motor * (2 * math.pi / 60.0)

                kt_si = 0.0
                kt_adc = 0.0

                if abs(omega_motor) > 1.0: # Avoid noise/stiction
                    # 1. Calculate Kt (SI) using True DC Current
                    v_ir_si = avg_i_true_dc_motor * MOTOR_RESISTANCE_OHM
                    bemf_si = v_app - v_ir_si
                    kt_si = bemf_si / omega_motor

                    # 2. Calculate Kt (ADC) using Observed ADC Current
                    v_ir_adc = avg_cs_right * MOTOR_RESISTANCE_OHM
                    bemf_adc = v_app - v_ir_adc
                    kt_adc = bemf_adc / omega_motor

                # Log to console and file
                f.write(f"{pwm_cmd},{avg_rpm_output:.4f},{avg_voltage:.4f},{avg_cs_right:.4f},{avg_i_true_dc_motor:.4f},{v_app:.4f},{kt_si:.6f},{kt_adc:.6f}\n")
                print(f"{pwm_cmd:3d} | {avg_rpm_output:5.1f} | {avg_i_true_dc_motor:5.3f} | {avg_cs_right:5.3f} | {kt_si:.4f} | {kt_adc:.4f}")

            else:
                print(f"ERROR: Failed to get {AVERAGE_COUNT} valid reads at PWM {pwm_cmd}. Error: {error}")

        # 4. STOP MOTOR
        for _ in range(5):
            send_pwm_command(bus, 0, 0)
            time.sleep(COMMAND_PERIOD_SEC)

        print("\n--- Profiler Finished. Motor Stopped. ---")

#!/usr/bin/env python

from smbus2 import SMBus
import crc8

STATUS_BUFFER_SIZE = 32

with SMBus(1) as bus:

    try:
        # read status
        status = bus.read_i2c_block_data(0x3C, 0xA0, STATUS_BUFFER_SIZE)
        #print(status)
    except IOError as e:
        print('IOError: %s' % e)

    encoder_left = status[0] << 24 | status[1] << 16 | status[2] << 8 | status[3]
    encoder_right = status[4] << 24 | status[5] << 16 | status[6] << 8 | status[7]
    print('encoder_left: {}'.format(encoder_left))
    print('encoder_right: {}'.format(encoder_right))

    bus_current_raw = status[8] << 8 | status[9]
    bus_voltage_raw = status[10] << 8 | status[11]

    # ina219_currentDivider_mA = 10.0
    bus_current_amps = bus_current_raw / (10.0 * 1000.0) # convert to amps
    print('bus current: {} A'.format(bus_current_amps))
    bus_voltage_volts = bus_voltage_raw / 1000.0 # convert to volts
    print('bus voltage: {} V'.format(bus_voltage_volts))

    # measured current left, right
    cs_left_raw = status[12] << 8 | status[13]
    cs_right_raw = status[14] << 8 | status[15]
    cs_left = cs_left_raw * (6.6 / 4095)        # 500mV/A
    cs_right = cs_right_raw * (6.6 / 4095)      # 500mV/A
    print('cs: {}, {}'.format(cs_left, cs_right))

    # control effort
    pwm_left = status[16] << 8 | status[17]
    pwm_right = status[18] << 8 | status[19]
    print('pwm: {}, {}'.format(pwm_left, pwm_right))

    # motor direction (not encoder direction)
    dir_left = status[20] & 0x01 > 0
    dir_right = status[20] & 0x02 > 0
    print('pwm dir: {}, {}'.format(dir_left, dir_right))

    ROUNDS_PER_MINUTE = (60.0 / (1.0 / 10)) / (48 * 65)
    # current rpm raw values, multiply by ROUNDS_PER_MINUTE
    rpm_left = status[21] << 8 | status[22]
    rpm_right = status[23] << 8 | status[24]
    print('rpm: {}, {}'.format(rpm_left * ROUNDS_PER_MINUTE, rpm_right * ROUNDS_PER_MINUTE))

    # encoder dir values
    enc_dir_left = (status[25] & 0x0F) - 1
    enc_dir_right = ((status[25] & 0xF0) >> 4) - 1
    print('enc dir: {}, {}'.format(enc_dir_left, enc_dir_right))

    # print the statuses
    print('STATUS: [{}, {}, {}]'.format(status[26], status[27], status[28]))

    # human readable power status
    power_status = status[26]
    _power_status = ''
    if power_status & 0x80:
        _power_status += 'CMD_TIMEOUT | '
    if power_status & 0x20:
        _power_status += 'RIGHT AMP LIMIT | '
    if power_status & 0x10:
        _power_status += 'LEFT AMP LIMIT | '
    if power_status & 0x08:
        _power_status += 'MAIN AMP LIMIT | '
    if power_status & 0x04:
        _power_status += 'BAT VOLTS HIGH | '
    if power_status & 0x02:
        _power_status += 'BAT VOLTS LOW | '
    if power_status & 0x01:
        _power_status += 'AUX CTL ON | '

    _power_status_len = len(_power_status)
    if _power_status_len:
        print('POWER_STATUS:', _power_status[0:_power_status_len - 3])

    # human readable motor status
    motor_status = status[27]
    _motor_status = 'MOTOR_STATUS: '

    if motor_status & 0x80:
        _motor_status += 'FLT RIGHT | '
    if motor_status & 0x40:
        _motor_status += 'FLT LEFT | '

    if motor_status & 0x20:
       _motor_status += 'FWD RIGHT | '
    else:
       _motor_status += 'REV RIGHT | '

    if motor_status & 0x10:
       _motor_status += 'FWD LEFT | '
    else:
       _motor_status += 'REV LEFT | '

    if motor_status & 0x04:
       _motor_status += 'MODE1 | '

    if motor_status & 0x08:
       _motor_status += 'MODE2 | '

    drive_mode = (motor_status & 0x01) + (motor_status & 0x02);

    _motor_status += 'DRIVE = '
    _motor_status += str(drive_mode)

    print(_motor_status)

    # human readable system status
    system_status = status[28]
    _system_status = ''

    if system_status & 0x80:
        _system_status += 'EEPROM_INIT_ERROR | '

    if system_status & 0x40:
        _system_status += 'REBOOT_REQUIRED |'

    if system_status & 0x01:
        _system_status += 'EEPROM_WRITE_I2C_ERROR | '

    _system_status_len = len(_system_status)
    if _system_status_len:
        print('SYSTEM_STATUS:', _system_status[0:_system_status_len - 3])

    deltaT = status[30]
    print('packet age: %s ms' % deltaT)

    print('packet sequence: %s' % status[29])

    packet_checksum = status[31]

    hash = crc8.crc8()
    hash.update(bytearray(status[0:30]))
    calculated_checksum = int(hash.hexdigest(), 16)

    if calculated_checksum != packet_checksum:
      print('packet checksum: %s' % packet_checksum)
      print('calculated checksum: %s' % calculated_checksum)
      print('INVALID CHECKSUM')
    else:
      print('VALID CHECKSUM')


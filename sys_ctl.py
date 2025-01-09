#!/usr/bin/env python

import sys
import string
from smbus2 import SMBus


DEVICE_ADDR = 0x3c

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

with SMBus(1) as bus:

   if len(sys.argv) != 2:
       print('incorrect arguments')
       print('SYSCTL_CODE_RESET 0x01')
       print('SYSCTL_CODE_SOFTRESET 0x02')
       print('SYSCTL_CODE_ENCODER_RESET 0x04')
       print('SYSCTL_CODE_HIBERNATE 0x05')
       print('SYSCTL_CODE_PRINT_PARAMETERS 0x06')
       print('SYSCTL_CODE_PRINT_STATUS 0x07')
       print('SYSCTL_CODE_RECORD_PID 0x08')
       print('SYSCTL_CODE_PRINT_KPID 0x09')
       print('SYSCTL_CODE_DIR_LEFT_FWD 0x30')
       print('SYSCTL_CODE_DIR_LEFT_REV 0x31')
       print('SYSCTL_CODE_DIR_RIGHT_FWD 0x32')
       print('SYSCTL_CODE_DIR_RIGHT_REV 0x33')
       print('SYSCTL_CODE_DIR_BOTH_FWD 0x34')
       print('SYSCTL_CODE_DIR_BOTH_REV 0x35')
       print('SYSCTL_CODE_MODE1_ON 0x40')
       print('SYSCTL_CODE_MODE1_OFF 0x41')
       print('SYSCTL_CODE_MODE2_ON 0x42')
       print('SYSCTL_CODE_MODE2_OFF 0x43')
       print('SYSCTL_CODE_AUX_ON 0x50')
       print('SYSCTL_CODE_AUX_OFF 0x51')
       print('SYSCTL_CODE_FACTORY_DEFAULTS 0x99')
       print('SYSCTL_CODE_PRINT_RTC 0xAA')

       exit(0)

   if not sys.argv[1].startswith('0x') and is_hex(sys.argv[1]):
      print('incorrect command')
      exit(0)

   command = int(sys.argv[1], 16)

   if command > 0xFF:
      print('incorrect command')
      exit(0)

   try:
      # 0x04 is sys_ctl address
      bus.write_i2c_block_data(DEVICE_ADDR, 0x04, [0,0,0,command])
   except IOError as e:
      print('IOError: %s' % e)


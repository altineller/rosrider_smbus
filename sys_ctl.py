#!/usr/bin/env python

import sys
import string
from smbus2 import SMBus

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

with SMBus(1) as bus:

   if len(sys.argv) != 2:
       print('incorrect arguments')
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
      bus.write_i2c_block_data(0x3C, 0x04, [0,0,0,command])
   except IOError as e:
      print('IOError: %s' % e)


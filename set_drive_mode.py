#!/usr/bin/env python


DEVICE_ADDR = 0x3c

import sys
import string
from smbus2 import SMBus

with SMBus(1) as bus:

   if len(sys.argv) != 2:
       print('incorrect arguments')
       exit(0)

   mode = int(sys.argv[1], 16)

   if mode not in range(4):
       print('incorrect mode')
       exit(0)

   try:
       # 0x05 is set_drive_mode address
       bus.write_i2c_block_data(DEVICE_ADDR, 0x05, [0,0,0,mode])
   except IOError as e:
       print('IOError: %s' % e)




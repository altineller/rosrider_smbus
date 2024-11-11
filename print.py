#!/usr/bin/env python

import struct
import time


posix_time = int(time.time())

print(posix_time)

print(bytearray(struct.pack("i", posix_time)))

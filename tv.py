#!/usr/bin/env python3

import pytv
import time


tvcmd = pytv.tvControl("192.168.1.55",8080,"676905")

tvcmd.connect()

tvcmd.handleCommand("VOLUP")

time.sleep(3)

tvcmd.handleCommand("VOLDN")

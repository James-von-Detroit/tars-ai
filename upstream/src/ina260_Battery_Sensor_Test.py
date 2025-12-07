# SPDX-License-Identifier: CC-BY-NC-4.0
# Copyright (c) TARS-AI Community
# Licensed under Creative Commons Attribution-NonCommercial 4.0 International
#
# Original source: https://github.com/TARS-AI-Community/TARS-AI
# This file may not be used for commercial purposes.

import time
from modules.module_battery import BatteryModule

battery = BatteryModule()
battery.start()

while True:
    print(battery.get_battery_status())
    time.sleep(1)
    
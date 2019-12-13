#!/bin/bash

# 禁止cpu降频
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null



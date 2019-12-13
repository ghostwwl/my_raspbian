#!/bin/bash

# 禁止cpu降频
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null

#cpupower frequency-set -g performance
#cpupower frequency-set -d 1.5GHz
#cpupower frequency-set -u 1.5GHz


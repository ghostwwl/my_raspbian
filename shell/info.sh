#!/bin/sh

# 当前cpu温度
echo 'CPU 温度:' `vcgencmd measure_temp`

# 当前cpu频率
echo 'CPU 频率:' `sudo cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq` 'Hz'

# 当前cpu电压
echo 'CPU 电压:' `vcgencmd measure_volts`

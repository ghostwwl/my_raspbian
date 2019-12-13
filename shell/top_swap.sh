#!/bin/bash

ps ax | sed "s/^ *//" > /tmp/ps_ax.output
for x in `grep Swap /proc/[1-9]*/smaps | grep -v '0 kB' | tr -s ' ' | cut -d' ' -f-2 | sort -t' ' -k2 -n | tr -d ' ' | tail -10`; do
    swapusage=`echo $x | cut -d: -f3`
    pid=`echo $x | cut -d/ -f3`
    procname=`cat /tmp/ps_ax.output | grep ^$pid`
    echo "============================"
    echo "Process :$procname"
    echo "Swap usage: $swapusage kB"
done

rm -f /tmp/ps_ax.output


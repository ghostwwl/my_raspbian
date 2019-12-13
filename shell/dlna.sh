#!/bin/sh


function_start_dlna()
{
	printf "Starting MiniDlna...\n"
	minidlnad -f /etc/minidlna.conf -P /home/pi/dlna/minidlna.pid -r -L
}

function_stop_dlna()
{
	printf "Stoping MiniDlna...\n"
	if [ -f /home/pi/dlna/minidlna.pid ] ; then
		kill -15 `cat /home/pi/dlna/minidlna.pid`
	else
		kill -15 $(ps -ef|grep 'minidlnad'|grep -v 'grep'|awk '{printf $2}')
	fi
}

if [ "$1" = "start" ]; then
	function_start_dlna
elif [ "$1" = "stop" ]; then
	function_stop_dlna
elif [ "$1" = "restart" ]; then
	function_stop_dlna
	function_start_dlna
else
	printf "Usage: dlna.sh {start|stop|restart}\n"
fi


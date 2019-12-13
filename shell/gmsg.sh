#!/bin/bash

#/* ****************************************************
# * FileName: gmsg.sh
# * Author  : ghostwwl
# * Date    : 2015
# * Note    : message output for posix shell
# * ***************************************************/


function color_msg ()
{

	black='\033[0m'
	boldblack='\033[1;0m'
	red='\033[31m'
	boldred='\033[1;31m'
	green='\033[32m'
	boldgreen='\033[1;32m'
	yellow='\033[33m'
	boldyellow='\033[1;33m'
	blue='\033[34m'
	boldblue='\033[1;34m'
	magenta='\033[35m'
	boldmagenta='\033[1;35m'
	cyan='\033[36m'
	boldcyan='\033[1;36m'
	white='\033[37m'
	boldwhite='\033[1;37m'

	local default_msg="No message passed."
	message=${1:-$default_msg}
	color=${2:-black}

	case $color in
		black)
			printf "$black" 
			;;
		boldblack)
			printf "$boldblack"
			;;
		red)
			printf "$red"
			;;
		boldred)
			printf "$boldred"
			;;
		green)
			printf "$green"
			;;
		boldgreen)
			printf "$boldgreen"
			;;
		yellow)
			printf "$yellow"
			;;
		boldyellow)
			printf "$boldyellow"
			;;
		blue)
			printf "$blue"
			;;
		boldblue)
			printf "$boldblue"
			;;
		magenta)
			printf "$magenta"
			;;
		boldmagenta)
			printf "$boldmagenta"
			;;
		cyan)
			printf "$cyan"
			;;
		boldcyan)
			printf "$boldcyan"
			;;
		white)
			printf "$white"
			;;
		boldwhite)
			printf "$boldwhite"
			;;
		esac
		  	printf "%s\n"  "$message"
		  	tput sgr0			# Reset to normal.
		  	printf "$black"
		return
}

function message()
{

	dtag=`date '+%Y-%m-%d %H:%M:%S'`
	LEVE_KEY=('INFO' 'WARNING' 'ERROR' 'DEBUG' 'FATAL')
	level=${2:-1}
	leve_str=${LEVE_KEY[0]}
	
	if [ -n $level ]; then
		leve_str=${LEVE_KEY[`expr $level - 1`]}
	fi
    	Msg=$(printf "%-7s %s] %s\n" "${leve_str}" "${dtag}" "$1")
	case $level in
		"1")
			color_msg "$Msg" cyan
			;;
		"2")
			color_msg "$Msg" green
			;;
		"3")
			color_msg "$Msg" boldred
			;;
		"4")
			color_msg "$Msg" yellow
			;;
		"5")
			color_msg "$Msg" boldmagenta
		esac
			return
}

function seg()
{
	sencents=${1:-1}
	result=$(echo $sencent|python3 -m jieba)
	message "$result"
}

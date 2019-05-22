#!/bin/bash
PROGRAMNAME=`basename $0`

if [ $# -lt 2 -o $# -gt 3 ]
then
	echo 'Usage:'
	echo $PROGRAMNAME 'load (rule file) [unload file]'
	echo $PROGRAMNAME 'unload (unload file)'
	echo
	echo 'Ensure that rule or unload file is completely valid. Otherwise, the script will have an undefined behaviour.'
	echo 'This script does not perform any checks to the rule or unload file whatsoever.'
	echo
	echo 'The unload file is used to undo changes that were made using this script.'
	echo 'It can be ommited if user does not intend to unload the loaded rules.'
	echo
	echo 'Format of rule file is:'
	echo 'table_name,insert_mode,chain,iptables_rule'
	echo 'where:'
	echo ' - table_name is one of valid iptables table, such as "filter", "nat", etc.'
	echo ' - insert_mode is either "A" (add to end) or "I" (add to top).'
	echo ' - chain is the valid iptables chain name in the given table_name'
	echo ' - iptables_rule is the rule. This rule will be interpreted directly by system''s iptables'
	exit
fi

if [ ! -r "$2" ]
then
	echo Cannot access file "'$2'"
	exit 1
fi

cleanup () {
	sleep 5
	echo clean >> /log.txt
}

trap cleanup SIGINT SIGTERM

case "$1" in
	load)
		# does we have unload file set for writing?
		if [ $# -eq 3 ]
		then
			# first, check if we can write to the 'unload file'
			if >> "$3"
			then
				:
			else
				echo Cannot access file for writing "'$3'"
				exit 1
			fi
			# set the variable and empty it!
			UNLOADFILE="$3"
			> "$UNLOADFILE"
		fi
		# proceed to load the rule
		# prompt the time when the rule was loaded
		echo `date`: 'load iptables rule'
		# tokenize line by line
		IFS=$'\n'
		for RULE in `cat "$2"`
		do
			# non standard IFS interferes with shell execution
			unset IFS
			IFS=, read -r -a COMP <<< "$RULE"
			# don't load rule if it exists
			CMD=`echo iptables -t ${COMP[0]} -C ${COMP[2]} ${COMP[3]}`
			$CMD &> /dev/null
			# error code not 0 means that iptables could not find the rule. add it!
			if [ $? -ne 0 ]
			then
				CMD=`echo iptables -t ${COMP[0]} -${COMP[1]} ${COMP[2]} ${COMP[3]}`
				# echo to stdout
				echo 'load:' $CMD
				# run the command!
				$CMD
				# write to unload file if exists (using our own format)
				if [ ! -z "$UNLOADFILE" ]
				then
					echo ${COMP[0]},D,${COMP[2]},${COMP[3]} >> "$UNLOADFILE"
				fi
			fi
		done
		;;
	unload)
		echo `date`: 'unload iptables rule'
		# tokenize line by line
		IFS=$'\n'
		for RULE in `cat "$2"`
		do
			# non standard IFS interferes with shell execution
			unset IFS
			IFS=, read -r -a COMP <<< "$RULE"
			# build deletion command, in the same way as if we were to load the rule file
			# we're ignoring the command (2nd) field here
			CMD=`echo iptables -t ${COMP[0]} -D ${COMP[2]} ${COMP[3]}`
			# execute the command no matter what!
			$CMD
			echo 'unload:' $CMD
		done
		;;
	*)
		echo Invalid command
		exit 1
esac

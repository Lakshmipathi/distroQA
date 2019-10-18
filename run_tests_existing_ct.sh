#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Please provide running docker id and takfiles"
	exit
fi

did=$1

for i in {10..0..-1};
do
	printf "Please wait for $i seconds \\r"; sleep 1; printf \\r; 
done
printf \\r
shift

for task in "$@"
do
 	docker exec -it $did python3 /test/distroqa.py --taskfile $task
	sleep 2
done

# Clean up containers
# docker stop $did &> /dev/null
# docker rm $did &> /dev/null

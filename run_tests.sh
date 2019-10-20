#!/bin/bash

# Copyright © 2019 Collabora Ltd.
#
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

set -uex


if [ -n "${EXPOSE_PORT-}" ]; then
    USE_PORT=" -p :80 "
else
    USE_PORT=" "
fi

if [ -n "${GZ_FILE-}" ]; then
    GZ_FILE=${GZ_FILE:-}
else
    GZ_FILE=" "
fi

clear
DOCKER_OPTS=" --privileged --device /dev/kvm -itd  $USE_PORT "
DOCKER_OPTS=" $DOCKER_OPTS -e RESOLUTION=1920x1080 -e PYTHONIOENCODING=utf8 -e GZ_FILE=$GZ_FILE"
VOL_OPTS=" -v `pwd`:/test -v `pwd`/qemu:/qemu -v `pwd`/results:/results "

did=$(docker run $DOCKER_OPTS $VOL_OPTS laks/gui_tester:screen_recorder)

printf "Please wait for 10 seconds"; 
sleep 10

portnum=$(docker port $did | cut -f2 -d':')

printf \\r
printf -- "-----------------------------------------------------------\n"
printf "OS GUI automation started on container: %s \n" "${did:0:6}"
printf -- "-----------------------------------------------------------\n\n"

for task in "$@"
do
	docker exec -i "$did" python3 /test/distroqa.py --taskfile "$task" --no_verbose
	sleep 2
done

printf "\n Creating final video please wait...\n"
docker exec "$did" screen_recorder merge final_video &> /dev/null
docker exec "$did" /test/report.sh &> /dev/null

# Clean up containers
docker stop "$did" &> /dev/null
docker rm "$did" &> /dev/null

printf -- "-----------------------------------------------------------\n\n"
printf "See results/${did:0:12}/index.html for test status \n"
printf -- "-----------------------------------------------------------\n\n"

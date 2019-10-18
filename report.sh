#!/bin/bash
# Copyright © 2019 Collabora Ltd.
#
# SPDX-License-Identifier: MIT
#

# Generate HTML log report from resulting image and video files.

INDEXFILE="/results/$(hostname)/index.html"
STATUSFILE="/results/$(hostname)/test_failed"


setup_header() {
cat << EOF > $INDEXFILE
<!DOCTYPE html> <html> <body> <table width='1500'  border='1'  cellpadding='3'><tr>
EOF
}

setup_footer() {
cat << EOF >> $INDEXFILE
</tr></table></body></html>
EOF
}

setup_headername() {
	td_entry='
	<tr bgcolor="#FFA07A"><td align="center" valign="center">
	'$1'
	</td></tr>'

cat << EOF >> $INDEXFILE
${td_entry}
EOF
}

check_status() {
	if [ ! -f $STATUSFILE ]; then
		clr="#008000"
		res="PASS"
	else
		clr="#FF0000"
		res="FAIL"
	fi

	td_entry='
	<tr bgcolor="'$clr'"><td align="center" valign="center">
	'$res'
	</td></tr>'

cat << EOF >> $INDEXFILE
${td_entry}
EOF
}

image_data() {
	fn=$1
	fn_desc=$(basename $fn)

	td_entry='
	<td align="center" valign="center">
	<a target="_blank" href="'$fn'">
	<img src="'$fn'" width="300px" />
	</a>
	<br />
	'$fn_desc'
	</td>'
cat << EOF >> $INDEXFILE
${td_entry}
EOF
}

video_data() {
	fn=$1
	fn_desc=$(basename $fn)

	td_entry='
	<td align="center" valign="center">
	<video width="300" controls>
	<source src="'$fn'" type="video/mp4">
	</video>
	<br />
	'$fn_desc'
	</td></tr><tr>'

cat << EOF >> $INDEXFILE
${td_entry}
EOF
}

prepare_report() {
files=`find /results/$(hostname) -type f -exec ls -1rt "{}" +; `
files_list=(${files})

dirs=`find /results/$(hostname)/* -type d -exec ls -1d "{}" +;`
dir_list=(${dirs})

for d in "${dir_list[@]}"; do 
	echo $(basename $d) 
done

for fn in "${files_list[@]}"; do
case "$fn" in 
  *png*)
      f=$(basename $(dirname $fn))/$(basename $fn)
      image_data $f
      ;;
  *mp4*)
      f=$(basename $(dirname $fn))/$(basename $fn)
      video_data $f
      hdr=$(dirname $fn)
      setup_headername $(basename $hdr)
      ;;
esac
done
}

setup_header
prepare_report
check_status
setup_footer


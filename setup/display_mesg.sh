#!/bin/bash
set -u

if [ ! -d ~/.magick ] ; then 
mkdir -p ~/.magick && cd ~/.magick
cp /mnt/setup/type_gen ~/.magick
find /usr/share/fonts -name "*.[to]tf" | perl /mnt/setup/type_gen -f - > type.xml
sleep 2
fi

MSG=${1:-}
rm -f /tmp/result.png
convert -size 360x120 xc:white  -pointsize 122 -fill red -draw "text 50,95 '${MSG}'" /tmp/result.png && timeout 30 display /tmp/result.png &
sleep 2

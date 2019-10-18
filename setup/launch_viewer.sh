#!/bin/bash
set -xu
apt-get install wmctrl xdotool -y
term_id=$(xdotool getactivewindow)
remote-viewer spice://localhost:5924 &
pid=$!
sleep 2
wid=$(wmctrl -lp | grep ${pid} | cut "-d " -f1)
sleep 3
xdotool windowmove ${wid} 10 10
# Minimize current terminal
xdotool windowminimize $term_id

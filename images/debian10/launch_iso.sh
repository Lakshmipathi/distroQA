#!/bin/bash

set -ue
ISO_FILE="debian-10.1.0-amd64-xfce-CD-1.iso"
DISK_IMAGE="debian10.raw"
SPICE_PORT=5924

qemu-img create -f raw "$DISK_IMAGE" 10G

apt-get install wget -y
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-10.1.0-amd64-xfce-CD-1.iso

qemu-system-x86_64 \
	-cdrom "${ISO_FILE}" \
        -drive file=${DISK_IMAGE:?},cache=none,if=virtio \
        -m 2G \
        -smp 2 \
        -vga qxl \
        -serial mon:stdio \
        -net user,hostfwd=tcp::2222-:22 \
	-net nic \
        -spice port=${SPICE_PORT:?},disable-ticketing \
        -device virtio-serial-pci \
        -device virtserialport,chardev=spicechannel0,name=com.redhat.spice.0 \
        -chardev spicevmc,id=spicechannel0,name=vdagent 

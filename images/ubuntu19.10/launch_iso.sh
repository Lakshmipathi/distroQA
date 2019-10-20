#!/bin/bash

set -ue
ISO_FILE="eoan-desktop-amd64.iso"
DISK_IMAGE="ubuntu19.10.raw"
SPICE_PORT=5924

qemu-img create -f raw "$DISK_IMAGE" 10G

apt-get install wget -y
wget http://cdimages.ubuntu.com/daily-live/current/eoan-desktop-amd64.iso

qemu-system-x86_64 \
	-enable-kvm \
	-cdrom "${ISO_FILE}" \
        -drive file=${DISK_IMAGE:?},cache=none,if=virtio \
        -m 4G \
        -smp 2 \
        -vga std \
        -serial mon:stdio \
        -net user,hostfwd=tcp::2222-:22 \
	-net nic \
        -spice port=${SPICE_PORT:?},disable-ticketing \
        -device virtio-serial-pci \
        -device virtserialport,chardev=spicechannel0,name=com.redhat.spice.0 \
        -chardev spicevmc,id=spicechannel0,name=vdagent 

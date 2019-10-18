set -ue
ISO_FILE="debian-testing-amd64-xfce-CD-1.iso"
DISK_IMAGE="debian.img"
SPICE_PORT=5924

qemu-system-x86_64 \
	-cdrom "${ISO_FILE}" \
        -drive format=raw,if=pflash,file=/usr/share/ovmf/OVMF.fd,readonly \
        -drive file=${DISK_IMAGE:?} \
        -enable-kvm \
        -m 1G \
        -smp 2 \
        -cpu host \
        -vga qxl \
        -serial mon:stdio \
        -net user,hostfwd=tcp::2222-:22 \
	-net nic \
        -spice port=${SPICE_PORT:?},disable-ticketing \
        -device virtio-serial-pci \
        -device virtserialport,chardev=spicechannel0,name=com.redhat.spice.0 \
        -chardev spicevmc,id=spicechannel0,name=vdagent 

#!/bin/bash

if [ "$1" -eq 0 ]; then
    if grep -q 0 "/sys/devices/70090000.xusb/downgrade_usb3"; then exit 0; else exit 1; fi
elif [ "$1" -eq 1 ]; then
    echo 0 > /sys/devices/70090000.xusb/downgrade_usb3
elif [ "$1" -eq 2 ]; then
    echo 0xffffffff > /sys/devices/70090000.xusb/downgrade_usb3
elif [ "$1" -eq 3 ]; then
     echo "[$2] $3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0" > /sys/devices/thermal-fan-est/coeff
elif [ "$1" -eq 4 ]; then
     if grep -q 0 "/var/lib/nvpmodel/auto_profiles"; then exit 0; else exit 1; fi
elif [ "$1" -eq 5 ]; then
     echo $2 > /var/lib/nvpmodel/auto_profiles
fi
    
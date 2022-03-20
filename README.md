Linux configs for the Nintendo Switch
=====================================

## Currently contains:

  * switch-dock-handler - Toggles display and audio when the console is docked.
  * switch-dconf-customizations - Various customizations to programs for the switch.
  * switch-alsa-ucm - ALSA UCM1 configurations to support headphones and speakers.
  * switch-alsa-ucm2 - ALSA UCM2 configurations to support headphones/mic and speakers.
  * switch-bluetooth-service - Service to load the firmware to the switches bluetooth chip.
  * switch-r2p-service - Reboot to Payload service by default reboot to Hekate bootloader.
  * switch-xorg-conf - Xorg monitor configuration.
  * switch-upower - Upower service for battery indicator.
  * switch-sddm-rule - SDDM udev rule that.

## File mapping:
`switch-dock-handler/92-dp-switch.rules usr/lib/udev/rules.d`
`switch-dock-handler/dock-hotplug usr/bin`

`switch-dconf-customizations/99-switch etc/dconf/db/local.d`
`switch-dconf-customizations/user etc/dconf/profile`

`switch-alsa-ucm/tegra-snd-t210ref-mobile-rt565x.conf usr/share/alsa/ucm/tegra-snd-t210ref-mobile-rt565x`
`switch-alsa-ucm/HiFi usr/share/alsa/ucm/tegra-snd-t210ref-mobile-rt565x`

`switch-alsa-ucm2/tegra-snd-t210r.conf /usr/share/alsa/ucm2/tegra-snd-t210r/tegra-snd-t210r.conf`
`switch-alsa-ucm2/HiFi.conf /usr/share/alsa/ucm2/tegra-snd-t210r/HiFi.conf`

`switch-bluetooth-service/switch-bluetooth.service usr/lib/systemd/system`

`switch-touch-rules/* usr/lib/udev/rules.d`

`switch-r2p-service/r2p.service etc/systemd/system/`

`switch-xorg-conf/10-monitor.conf etc/X11/xorg.conf.d/`

`switch-upower/upower.service etc/systemd/system/`

`switch-sddm-rule/69-nvidia-seat.rules usr/lib/udev/rules.d/`

## Contributing:
All changes must be accompanied with and update to the projects VERSION file and
a package update on the debian branch.

Linux configs for the Nintendo Switch
=====================================

## Currently contains:

  * switch-dock-handler - Toggles display and audio when the console is docked.
  * switch-dconf-customizations - Various customizations to programs for the switch.
  * switch-alsa-ucm - ALSA UCM configurations to support headphones and speakers.

## File mapping:
`switch-dock-handler/92-dp-switch.rules usr/lib/udev/rules.d`
`switch-dock-handler/dock-hotplug usr/bin`
`switch-dconf-customizations/99-switch etc/dconf/db/local.d`
`switch-alsa-ucm/* usr/share/alsa/ucm/tegra-snd-t210ref-mobile-rt565x`

## Contributing:
All changes must be accompanied with and update to the projects VERSION file

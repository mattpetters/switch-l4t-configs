#!/usr/bin/env python3
#
# Copyright (c) 2019, NVIDIA CORPORATION.  All Rights Reserved.
# Copyright (c) 2021, CTCaer.  All Rights Reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import signal
import gi
import nvpmodel as nvpm
import subprocess
import time
import threading
import re
import sys

gi.require_version("Gtk", "3.0")
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject

INDICATOR_ID = 'nvpmodel'
ICON_DEFAULT = os.path.abspath('/usr/share/nvpmodel_indicator/nv_logo.svg')

nvpmodel_helper_path = "/usr/share/nvpmodel_indicator/nvpmodel_helper.sh"

GET_USB3_DISABLED = '0'
SET_USB3_ENABLE = '1'
SET_USB3_DISABLE = '2'
SET_FAN_COEFF = '3'
GET_AUTO_PROFILES = '4'
SET_AUTO_PROFILES = '5'

FAN_DEV1 = '0'
FAN_DEV2 = '1'

notify_disable = False
usb3_disable = False
auto_profiles = False

def confirm_reboot():
    dialog = gtk.MessageDialog(None, 0, gtk.MessageType.WARNING,
        gtk.ButtonsType.OK_CANCEL, "System reboot is required to apply changes")
    dialog.set_title("WARNING")
    dialog.format_secondary_text( "Do you want to reboot NOW?")
    response = dialog.run()
    dialog.destroy()
    return response == gtk.ResponseType.OK

def set_power_mode(item, mode_id):
    if item.get_active() and mode_id != pm.cur_mode():
        success = pm.set_mode(mode_id, ['pkexec'])
        if not success and confirm_reboot():
            pm.set_mode(mode_id, ['pkexec'], force=True)
            return
        indicator.set_label(pm.get_name_by_id(pm.cur_mode()), INDICATOR_ID)

def set_fan_mode(item, mode_id):
    if item.get_active() and mode_id != fm.cur_mode():
        success = fm.set_mode(mode_id, ['pkexec'])
        if not success and confirm_reboot():
            fm.set_mode(mode_id, ['pkexec'], force=True)
            return

def do_tegrastats(_):
    cmd = "x-terminal-emulator -e pkexec tegrastats".split()
    subprocess.call(cmd)

def do_auto_profiles(self):
    global auto_profiles
    if auto_profiles == self.get_active():
        return
    auto_profiles = self.get_active()
    if auto_profiles:
        subprocess.call([nvpmodel_helper_path, SET_AUTO_PROFILES, '1'])
    else:
        subprocess.call([nvpmodel_helper_path, SET_AUTO_PROFILES, '0'])

def do_disable_usb3(self):
    global usb3_disable
    if usb3_disable == self.get_active():
        return
    dialog = gtk.MessageDialog(None, 0, gtk.MessageType.WARNING,
        gtk.ButtonsType.OK_CANCEL, "This will disconnect all USB devices!")
    dialog.set_title("WARNING")
    dialog.format_secondary_text( "Do you want to continue?")
    response = dialog.run()
    dialog.destroy()
    if response == gtk.ResponseType.OK:
        usb3_disable = self.get_active()
        if usb3_disable:
            subprocess.call([nvpmodel_helper_path, SET_USB3_DISABLE])
        else:
            subprocess.call([nvpmodel_helper_path, SET_USB3_ENABLE])
    else:
        self.set_active(usb3_disable)

def quit(_):
    running.clear()
    gtk.main_quit()

def build_menu():
    global item_throttle_evt
    global usb3_disable
    global main_menu

    menu = gtk.Menu()
    main_menu = menu

    item_pm = gtk.MenuItem('Power modes:')
    item_pm.set_sensitive(False)
    menu.append(item_pm)

    group = []
    for mode in pm.power_modes():
        label = mode.id + ': ' + mode.name
        item_mode = gtk.RadioMenuItem.new_with_label(group, label)
        group = item_mode.get_group()
        item_mode.connect('activate', set_power_mode, mode.id)
        menu.append(item_mode)

    item_sep = gtk.SeparatorMenuItem()
    menu.append(item_sep)

    item_fm = gtk.MenuItem('Fan modes:')
    item_fm.set_sensitive(False)
    menu.append(item_fm)

    fgroup = []
    for mode in fm.fan_modes():
        label = mode.id + ': ' + mode.name
        item_mode = gtk.RadioMenuItem.new_with_label(fgroup, label)
        fgroup = item_mode.get_group()
        item_mode.connect('activate', set_fan_mode, mode.id)
        menu.append(item_mode)

    item_sep = gtk.SeparatorMenuItem()
    menu.append(item_sep)

    item_setting = gtk.MenuItem('Settings:')
    item_setting.set_sensitive(False)
    menu.append(item_setting)

    item_auto = gtk.CheckMenuItem('Automatic profiles')
    item_auto.connect('toggled', do_auto_profiles)
    menu.append(item_auto)
    auto_profiles = subprocess.call([nvpmodel_helper_path, GET_AUTO_PROFILES])
    if auto_profiles:
        item_auto.set_active(True);

    item_usb3 = gtk.CheckMenuItem('Disable USB3')
    item_usb3.connect('toggled', do_disable_usb3)
    menu.append(item_usb3)
    usb3_disable = subprocess.call([nvpmodel_helper_path, GET_USB3_DISABLED])
    if usb3_disable:
        item_usb3.set_active(True);

    item_sep = gtk.SeparatorMenuItem()
    menu.append(item_sep)

    item_tstats = gtk.MenuItem('Run tegrastats')
    item_tstats.connect('activate', do_tegrastats)
    menu.append(item_tstats)

    item_sep = gtk.SeparatorMenuItem()
    menu.append(item_sep)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    menu.show_all()
    return menu

def mode_change_monitor(running):
    global main_menu
    cur_mode = pm.cur_mode()
    cur_fmode = fm.cur_mode()
    pmode_changed = False
    fmode_changed = False
    while running.is_set():
        if cur_mode != pm.cur_mode():
            pmode_changed = True
            cur_mode = pm.cur_mode()
            # Let main thread do GUI things otherwise there can be conflicts.
            GObject.idle_add(
                indicator.set_label, pm.get_name_by_id(cur_mode), INDICATOR_ID,
                priority=GObject.PRIORITY_DEFAULT)
        if cur_fmode != fm.cur_mode():
            fmode_changed = True
            cur_fmode = fm.cur_mode()
            fan_dev1_coeff = fm.get_dev1_coeff_by_id(cur_fmode)
            fan_dev2_coeff = fm.get_dev2_coeff_by_id(cur_fmode)
            if fan_dev1_coeff != "" and fan_dev2_coeff != "":
                subprocess.call([nvpmodel_helper_path, SET_FAN_COEFF, FAN_DEV1, fan_dev1_coeff])
                subprocess.call([nvpmodel_helper_path, SET_FAN_COEFF, FAN_DEV2, fan_dev2_coeff])
        # Update active modes in menu
        if pmode_changed or fmode_changed:
            child = None
            fan_modes = False
            for child in main_menu.get_children():
                label = child.get_label()
                if not fan_modes and pmode_changed and label and label[0] == cur_mode:
                    pmode_changed = False
                    # Let main thread do GUI things otherwise there can be conflicts.
                    GObject.idle_add(child.set_active, True, priority=GObject.PRIORITY_DEFAULT)
                if fan_modes and fmode_changed and label and label[0] == cur_fmode:
                    fmode_changed = False
                    # Let main thread do GUI things otherwise there can be conflicts.
                    GObject.idle_add(child.set_active, True, priority=GObject.PRIORITY_DEFAULT)
                if label == 'Fan modes:':
                    fan_modes = True
        time.sleep(2)

pm = nvpm.nvpmodel()
fm = nvpm.nvfmodel()

# Unity panel strips underscore from indicator's label, replace '_' with
# space here so that name of power modes will be more readable.
for mode in pm.power_modes():
    mode.name = mode.name.replace('_', ' ')

for mode in fm.fan_modes():
    mode.name = mode.name.replace('_', ' ')

# AppIndicator3 doesn't handle SIGINT, wire it up.
signal.signal(signal.SIGINT, signal.SIG_DFL)

notify.init(INDICATOR_ID)
warning = notify.Notification.new("WARNING",
    "system is now being throttled", None)

power_mode = pm.cur_mode()
indicator = appindicator.Indicator.new(INDICATOR_ID, ICON_DEFAULT,
    appindicator.IndicatorCategory.SYSTEM_SERVICES)
indicator.set_label(pm.get_name_by_id(power_mode), INDICATOR_ID)
indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
main_menu = build_menu()
indicator.set_menu(main_menu)

# Set fan coeffs
fan_mode = fm.cur_mode()
fan_dev1_coeff = fm.get_dev1_coeff_by_id(fan_mode)
fan_dev2_coeff = fm.get_dev2_coeff_by_id(fan_mode)
if fan_dev1_coeff != "" and fan_dev2_coeff != "":
    subprocess.call([nvpmodel_helper_path, SET_FAN_COEFF, FAN_DEV1, fan_dev1_coeff])
    subprocess.call([nvpmodel_helper_path, SET_FAN_COEFF, FAN_DEV2, fan_dev2_coeff])

# Set active modes in menu
child = None
fan_modes = False
for child in main_menu.get_children():
    label = child.get_label()
    if not fan_modes and label and label[0] == power_mode:
        child.set_active(True)
    if fan_modes and label and label[0] == fan_mode:
        child.set_active(True)
    if label == 'Fan modes:':
        fan_modes = True

running = threading.Event()
running.set()
threading.Thread(target=mode_change_monitor, args=[running]).start()

gtk.main()

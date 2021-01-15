#!/usr/bin/python
import ptxconftools
from ptxconftools import ConfController
from ptxconftools.gtk import MonitorSelector
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3 as appindicator
import os

iconpath = os.path.dirname(ptxconftools.__file__) + "/iconStyle03_256.png"
APPINDICATOR_ID = "PTXConf"


class PTXConfUI:
    def __init__(self):
        # create systray interface
        self.systray = appindicator.Indicator.new(
            APPINDICATOR_ID, iconpath, appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.systray.set_status(appindicator.IndicatorStatus.ACTIVE)

        # construct menu
        menu = gtk.Menu()
        mitem = gtk.MenuItem(label="Configure")
        mitem.connect("activate", self.create_config_window)
        menu.append(mitem)
        mitem = gtk.MenuItem(label="Exit")
        mitem.connect("activate", self.exit_program)
        menu.append(mitem)
        menu.show_all()

        # attach menu to out system tray
        self.systray.set_menu(menu)

        # instantiate confcontroller
        self.config = ConfController()

    # def resetAllConfig(self, callback_data=None):
    #    self.myConf.resetAllDeviceConfig()

    def get_active_input(self):
        a = self.window.pt_dropdown.get_active_text()
        b = self.window.pt_dropdown.get_active()
        if b > 0:
            return a

    def get_selected_monitor(self, callback_data=None):
        a = self.window.monitor_dropdown.get_active_text()
        b = self.window.monitor_dropdown.get_active()
        if b > 0:
            return a

    def map_tablet_monitor(self, callback_data=None):
        # find ids for the right input device
        pen = self.get_active_input()
        # get the display width, screen_width and screen_offset for CTMGenerator function to calculate matrix
        monitor = self.get_selected_monitor()
        # call API with these settings
        self.config.set_pen_to_monitor(pen, monitor)

    def exit_program(self, callback_data=None):
        # This function kills the program PTXConf.
        # Can be called from 2 places, 1 from the appindicator dropdown menu "Exit",
        # another from the config popup window "Exit" button.
        gtk.main_quit()

    def create_config_window(self, callback_data=None):
        # first refress all monitor and touch/pen information
        self.config.refresh()

        # This creats a popup window for more detailed configuration if user find necessary.
        # Still incomplete at the moment.
        self.window = gtk.Window()
        # self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_border_width(20)
        self.window.set_title("PTXConf")
        self.window.connect("destroy", self.destroy_config_window)

        button_apply = gtk.Button.new_with_label("Apply")
        button_close = gtk.Button.new_with_label("Close")
        button_close.connect("clicked", self.destroy_config_window)

        vbox_root = gtk.Box.new(gtk.Orientation.VERTICAL, 20)
        hbox_buttons = gtk.ButtonBox.new(gtk.Orientation.HORIZONTAL)

        label_pointer = gtk.Label.new("Pointer device")
        label_monitor = gtk.Label.new("Monitor")

        # create monitor selector widget
        mon_selector = MonitorSelector(self.config.monitor_ids)

        # dropdown menus 1 and 2, users choose what input device map to what monitor.
        ptr_dropdown = gtk.ComboBoxText()
        ptr_dropdown.set_tooltip_text("Choose an input device to configure")
        # getting the list of names of the input device
        # set up the dropdown selection for input devices
        ptr_dropdown.append_text("")
        for i in self.config.pen_touch_ids:
            ptr_dropdown.append_text(i.decode() if isinstance(i, bytes) else i)
        ptr_dropdown.set_active(0)
        ptr_dropdown.connect("changed", self.get_active_input)
        
        # create and set up dopdownmenu 2: user select from a list of connected display/output deivces.
        monitor_dropdown = gtk.ComboBoxText()
        monitor_dropdown.set_tooltip_text("Choose a monitor to map the input to")

        # getting the list of display names
        # set up the dropdown selection for monitors
        monitor_dropdown.append_text("")
        monitor_dropdown.mons = self.config.monitor_ids.keys()
        for key in monitor_dropdown.mons:
            monitor_dropdown.append_text(key.decode() if isinstance(key, bytes) else key)
        monitor_dropdown.set_active(0)
        monitor_dropdown.handler_id_changed = monitor_dropdown.connect(
            "changed", self.monitor_dropdown_callback
        )

        # connect apply button to function
        button_apply.connect("clicked", self.map_tablet_monitor)

        # inserting all widgets in place
        hbox_buttons.add(button_apply)
        hbox_buttons.add(button_close)

        grid = gtk.Grid(column_spacing=10, row_spacing=10)
        grid.set_column_homogeneous(True)
        grid.set_hexpand(True)
        grid.attach(label_pointer, 0, 0, 1, 1)
        grid.attach(label_monitor, 0, 1, 1, 1)
        grid.attach(ptr_dropdown, 1, 0, 1, 1)
        grid.attach(monitor_dropdown, 1, 1, 1, 1)

        vbox_root.pack_start(mon_selector, False, False, 0)
        vbox_root.pack_start(grid, False, False, 0)
        vbox_root.pack_start(hbox_buttons, False, False, 0)
        self.window.add(vbox_root)
        self.window.show_all()

        # store convenient handle to drop down boxes
        self.window.monitor_selector = mon_selector
        self.window.monitor_selector.connect(
            "button-press-event", self.monitor_selector_callback
        )
        self.window.pt_dropdown = ptr_dropdown
        self.window.monitor_dropdown = monitor_dropdown

    def monitor_dropdown_callback(self, callback_data=None):
        # update MonitorSelector
        mon = self.window.monitor_dropdown.get_active_text()
        if mon in self.window.monitor_selector.moninfo:
            self.window.monitor_selector.set_active_mon(mon)

    def monitor_selector_callback(self, widget, event):
        # get mon selector selection
        mon_selection = self.window.monitor_selector.get_active_mon()
        # if different than drop down, update drop down
        if mon_selection != self.window.monitor_dropdown.get_active_text():
            # lookup this monitor index in drop down and set it...
            idx = list(self.window.monitor_dropdown.mons).index(mon_selection)
            # careful to disable dropdown changed callback while doing this
            hid = self.window.monitor_dropdown.handler_id_changed
            self.window.monitor_dropdown.handler_block(hid)
            self.window.monitor_dropdown.set_active(idx + 1)
            self.window.monitor_dropdown.handler_unblock(hid)

    def destroy_config_window(self, callback_data=None):
        # close the popup window, app will still be docked on top menu bar.
        self.window.destroy()

    def main(self):
        gtk.main()


import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)
p = PTXConfUI()
p.create_config_window()
# p.window.connect("destroy", gtk.main_quit)
p.main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# 在原来的基础上,增加以下功能：
# 1. 以可配置的方式显示相应的历史信息
# 
# seealso: README 
# Date:
# Author： mattmonkey <mattmonkey@sina.com> 
#
# Very simple app-indicator, shows gtk-bookmarks (aka places)
# Original Author: Alex Simenduev <shamil.si@gmail.com>

import os
import gtk
import gio
import signal
import subprocess
import appindicator
import urllib
from placesconfig import make_config, path_recentlyused, path_config

APP_NAME = 'indicator-placesplus'
APP_VERSION = '0.1'

class IndicatorPlaces:
	BOOKMARKS_PATH = os.getenv('HOME') + '/.gtk-bookmarks'

	def __init__(self):
		self.ind = appindicator.Indicator("places", "nautilus", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)        

		self.update_menu()

	def create_menu_item(self, label, icon_name):
		image = gtk.Image()
		image.set_from_icon_name(icon_name, 24)

		item = gtk.ImageMenuItem()
		item.set_label(label)
		item.set_image(image)
		item.set_always_show_image(True)
		return item

	def create_submenu(self, menu, label, icon_name):
		submenu = gtk.Menu()
		item = self.create_menu_item(label,icon_name)
		menu.append(item)
		item.set_submenu(submenu)
		return submenu


	# This method gets a themed icon name
	def get_bookmark_icon(self, path):
		if path.startswith("smb") or path.startswith("ssh") or path.startswith("ftp") or path.startswith("network"):
			icon_name = "folder-remote"    
		else:
			f = gio.File(path)
		try:   
			info = f.query_info(gio.FILE_ATTRIBUTE_STANDARD_ICON)
			icon = info.get_icon()
			icon_name = icon.get_names()[0]
		except (gio.Error, NameError):
			icon_name = "folder"

		return icon_name

	def create_separator_menuitem(self,menu):
		item = gtk.SeparatorMenuItem()
		menu.append(item)

	def create_history_menus(self, menu) :
		menu_names = self.config.get_menus()
		for menu_name in menu_names:
			title,sp,icon =  menu_name.partition("=")
			submenu = self.create_submenu(menu ,title, icon)
			for menuitem in self.config.get_menuitems(menu_name):
				item =self.create_menu_item(menuitem.get_title(),self.get_bookmark_icon(menuitem.get_path()))
				item.connect("activate",self.on_bookmark2_click,menuitem.get_commandline())
				submenu.append(item)

	def on_bookmark2_click(self, widget, cli):
		subprocess.Popen(cli, shell = True)

	# This methind creates a menu
	def update_menu(self, widget = None, data = None):
		try:
			bookmarks = open(self.BOOKMARKS_PATH).readlines()
		except IOError:
			bookmarks = []        

		self.config = make_config()

		# Create menu
		menu = gtk.Menu()
		self.ind.set_menu(menu)

		# Create history menu
		self.create_history_menus(menu)

		# Home folder menu item
		item = self.create_menu_item("Home Folder", "user-home") 
		item.connect("activate", self.on_bookmark_click, os.getenv('HOME'))
		menu.append(item)

		# Computer menu item
		item = self.create_menu_item("Computer", "computer" )
		item.connect("activate", self.on_bookmark_click, 'computer:')
		menu.append(item)

		# Computer menu item
		item = self.create_menu_item("Network", "network-workgroup")
		item.connect("activate", self.on_bookmark_click, 'network:')
		menu.append(item)

		# Show separator
		item = gtk.SeparatorMenuItem()
		menu.append(item)

		# Populate bookmarks menu items
		for bm in bookmarks:
			path, label = bm.strip().partition(' ')[::2]
			if not label:
				label = os.path.basename(os.path.normpath(path))

			label = urllib.unquote(label)
			item = self.create_menu_item(label, self.get_bookmark_icon(path))
			item.connect("activate", self.on_bookmark_click, path)

			# Append the item to menu
			menu.append(item)

		# Show separator
		self.create_separator_menuitem(menu)

		# Quit menu item
		item = self.create_menu_item("Quit", "gtk-quit")
		item.connect("activate", gtk.main_quit)
		menu.append(item)

		# Show the menu
		menu.show_all()

	# Open clicked bookmark
	def on_bookmark_click(self, widget, path):
		# subprocess.Popen('/usr/bin/xdg-open %s' % path, shell = True)
		subprocess.Popen('/usr/bin/nautilus %s' % path, shell = True)

	def on_bookmarks_changed(self, filemonitor, file, other_file, event_type):
		if event_type == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
			print 'Bookmarks changed, updating menu...'
			self.update_menu()

if __name__ == "__main__":
	# Catch CTRL-C
	signal.signal(signal.SIGINT, lambda signal, frame: gtk.main_quit())

	# Run the indicator
	i = IndicatorPlaces()

	# Monitor bookmarks changes 
	files = [i.BOOKMARKS_PATH, path_recentlyused, path_config  ]
	for afile in files:
		target = gio.File(afile)
		monitor = target.monitor_file()
		monitor.connect("changed", i.on_bookmarks_changed)            

	# Main gtk loop
	gtk.main()

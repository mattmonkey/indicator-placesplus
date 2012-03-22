#!/usr/bin/python
# -*- coding: utf8 -*-
# 解析配置文件(.placesplus)和历史文件（recently-used.xbel）
#
# Date:
# Author: mattmonkey <mattmonkey@sina.com>

from ConfigParser import SafeConfigParser
from xml2obj import Xml2Obj, Element
from urllib import unquote, quote
from os.path import basename,join,expanduser,dirname
from os import getcwd

xml_path_app = "info/metadata/bookmark:applications/bookmark:application"
path_recentlyused = expanduser("~/.local/share/recently-used.xbel")
path_config= join(dirname(__file__),"placesplus")

class ConfigParser:
	"""
		完整存储配置文件信息
	"""

	def __init__(self, path) :
		self.info = {}
		scp = SafeConfigParser()
		scp.readfp(open(path))
		sections = scp.sections()
		for section in sections:
			options = scp.options(section)
			self.info[section] = options

	def get_sections(self):
		return self.info.keys()

	def get_items(self,name):
		if self.info.has_key(name):
			return self.info[name]
		else:
			return []


class PlacesConfig:
	'''
		TODO 根据配置对BookmarkBean排序
	'''

	def __init__(self, config, parser ):
		self.config = config
		self.parser = parser
	
	def get_menus(self):
		return self.config.get_sections()
	
	def get_menuitems(self, menu):
		menuitems = []
		for mimetype  in self.config.get_items(menu):
			menuitems = menuitems + self.parser.get_catalog(mimetype)	
		return map(lambda elm: BookmarkBean(elm), menuitems)

class BookmarkBean:
	'''
		TODO 实现完整的XBEL的Bean
	'''
	def __init__(self, elm):
		self.elm = elm
		self.href = self.elm.getAttribute("href");

	def get_title(self):
		return basename(self.get_path())

	def get_commandline(self):
		commandline = xpath(self.elm, xml_path_app).getAttribute("exec")
		commandline = commandline.replace("%U",self.href[7:])
		commandline = commandline.replace("%u",self.href[7:])
		commandline = commandline.replace("%f",basename(self.href[7:]))
		return unquote(commandline.encode("utf8"))[1:-1]

	def get_path(self):
		return unquote(self.href.encode("utf8"))[7:]


class PlacesXml2Obj(Xml2Obj):
		
	path_separator = "/"
	path_attr_type = "info/metadata/mime:mime-type"

	def __init__(self):
		self.catalogs = {}
		Xml2Obj.__init__(self)

	def EndElement(self,name):
		if name == "bookmark" :
			
			curr_node = self.nodeStack[-1]
			attr_type =  xpath(curr_node, self.path_attr_type).getAttribute("type")
			
			if self.catalogs.has_key(attr_type):
				self.catalogs[attr_type].append(curr_node)
			else:
				self.catalogs[attr_type]=[curr_node]

		Xml2Obj.EndElement(self,name)
	

	def get_catalog(self,name):
		return self.catalogs.setdefault(name, [])


def xpath(elm,xpath):
	paths = xpath.split("/")
	tmp_elm = elm
	for path in paths:
		tmp_elm = tmp_elm.getElements(path)[0]
	return tmp_elm

def make_config():
	parser = PlacesXml2Obj()
	parser.Parse(expanduser(path_recentlyused))
	config = ConfigParser(path_config)
	return PlacesConfig(config,parser)

if __name__ == "__main__" :
	# 显示可用的
	config = make_config()
	print "setions of config file..."
	for menu in config.get_menus():
		print menu
	
	print 

	print "list of mimetype... "
	for mimetype in  config.parser.catalogs.keys():
		print mimetype


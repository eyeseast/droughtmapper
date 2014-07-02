#!/usr/bin/env python
"""
Render a US drought map using data from the [US Drought Monitor](http://droughtmonitor.unl.edu/)

Usage:

    $ droughtmap latest -o drought.png
"""
import datetime
import os
from xml.etree import ElementTree

import fiona
import mapnik
import requests


class DroughtMapper(object):
	"""
	Interface for creating drought maps

	Features:
	 - finds and downloads data from USDM
	 - reprojects shapefiles as needed (using fiona)
	 - caches projected shapefiles locally for later
	 - rasters map images according to a basic stylesheet
	"""
	def __init__(self, cache='.cache'):
		self.cache = os.path.realpath(cache)

	def get_latest_date(self, ignore_cache=False):
		"""
		Get the latest weekly date for which a shapefile is available from USDM.
		There's an XML set of stats here: http://droughtmonitor.unl.edu/tabular/total.xml

		Caches the result on the object.
		"""
		if getattr(self, '_latest_date', None) and not ignore_cache:
			return self._latest_date

		# grab what we need
		url = "http://droughtmonitor.unl.edu/tabular/total.xml"
		r = requests.get(url)
		
		# parse with ElementTree
		xml = ElementTree.fromstring(r.text)
		
		# first week is the latest
		# grab the date attribute
		week = xml.find('week')
		date = week.get('date')

		# cache the result and return a parsed date object
		self._latest_date = datetime.datetime.strptime(date, '%Y%m%d')
		return self._latest_date


	def get_shapefile(self, date, ignore_cache=False):
		"""
		Fetch and cache a shapefile from USDM (unless ignore_cache).

		Returns a path to a zipped shapefile (not an open file object)

		URL: http://droughtmonitor.unl.edu/data/shapefiles_m/USDM_20140624_M.zip
		"""
		url = date.strftime('http://droughtmonitor.unl.edu/data/shapefiles_m/USDM_%Y%m%d_M.zip')
		filename = os.path.basename(url)
		path = os.path.join(self.cache, 'zip', filename)
		dirname = os.path.dirname(path)
		
		if os.path.exists(path) and not ignore_cache:
			return path

		# go fetch the shapefile, and throw an error if something broke
		r = requests.get(url)
		r.raise_for_status()

		# mkdirs as needed
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		# if we get here we have a file
		with open(path, 'wb') as f:
			f.write(r.content)

		return path


	def get_us(self):
		"""
		Fetch and cache a shapefile for US states and land boundaries.
		"""

	def project_shapefile(self, shapefile):
		"""
		Reproject a shapefile into lat/lng
		"""

	def raster(self, shapefile, outfile, **options):
		"""
		Raster data from shapefile and write to outfile
		"""
		us = self.get_us()

	def render(self, date=None, outfile=None, **options):
		"""
		Render an image for date, writing to outfile.
		This is the main entrypoint for an instance,
		and running this should take care of all the intermediate steps.
		"""
		shapefile = self.get_shapefile(date)
		self.raster(shapefile, outfile, **options)


if __name__ == "__main__":
	dm = DroughtMapper()
	dm.render()
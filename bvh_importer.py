# 
# BVH Importer script for Maya.
# 
# Importer for .bvh files (BioVision Hierachy files).
# BVH is a common ascii motion capture data format containing skeletal and motion data.
# 
# <license>
# BVH Importer script for Maya.
# Copyright (C) 2012  Jeroen Hoolmans
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </license>

__author__ 		= "Jeroen Hoolmans"
__copyright__ 	= "Copyright 2012, Jeroen Hoolmans"
__credits__ 	= ["Jeroen Hoolmans"]
__license__ 	= "GPL"
__version__ 	= "1.0.0"
__maintainer__ 	= "Jeroen Hoolmans"
__email__ 		= "jhoolmans@gmail.com"
__status__ 		= "Production"

import pymel.core as pm
import maya.cmds as mc
import os, sys

class BVHImporterDialog(object):
	#
	# Dialog class..
	#
	def __init__(self):
		self._name = "bvhImportDialog"
		self._textfield = ""
		self._rootNode = None
		
		# BVH specific stuff
		self._filename = ""
		self._channels = []
		
		self.setup_ui()
	
	def setup_ui(self):
		win = self._name
		if mc.window(win, ex=True):
			mc.deleteUI(win)
		
		win = mc.window(self._name, w=200, rtf=True, sizeable=False)
		
		mc.columnLayout(adj=1)
		
		mc.rowLayout(adj=1, nc=2)
		self._textfield = mc.textField()
		mc.button("Select root", c=self._on_select_root)
		
		mc.setParent("..")
		mc.button("Import animation..", c=self._on_select_file)
		
		mc.window(win, e=True, rtf=True, sizeable=False)
		mc.showWindow(win)
		
	def _on_select_file(self, e):
		filter = "All Files (*.*);;Motion Capture (*.bvh)"
		dialog = mc.fileDialog2(fileFilter=filter, dialogStyle=2, fm=1)
		
		if not len(dialog):
			return
		
		self._filename = dialog[0]
		
		self._read_bvh()
		
	def _read_bvh(self):
		with open(self._filename) as f:
			print f[0]
			for line in f:
				if line.startswith("ROOT"):
					print line
		
	def _on_select_root(self, e):
		selection = pm.ls(sl=True)
		if len(selection) == 0:
			return
		self._rootNode = selection[0]
		mc.textField(self._textfield, e=True, text=str(self._rootNode))
		
if __name__ == "__main__":
	dialog = BVHImporterDialog()
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

translationDict = {
	"Xposition" : "translateX",
	"Yposition" : "translateY",
	"Zposition" : "translateZ",
	"Xrotation" : "rotateX",
	"Yrotation" : "rotateY",
	"Zrotation" : "rotateZ"
}


class TinyDAG(object):
	def __init__(self, obj, pObj = None):
		self.obj = obj
		self.pObj = pObj
		
	def __str__(self):
		return str(self.obj)

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
		level = 0
		myParent = None
		safeClose = False
		motion = False
		
		with open(self._filename) as f:
			# Check to see if the file is valid (sort of)
			if not f.next().startswith("HIERARCHY"):
				mc.error("No valid .bvh file selected.")
				return False
			
			for line in f:
				if not motion:
					# root joint
					if line.startswith("ROOT"):
						myParent = TinyDAG(line[5:].rstrip(), myParent)
						# strip newline
					
					if "JOINT" in line:
						jnt = line.split(" ")
						myParent = TinyDAG(jnt[-1].rstrip(), myParent)
						# strip newline
	
					if "End Site" in line:
						safeClose = True
	
					if "}" in line:
						if safeClose:
							safeClose = False
							continue
							
						if myParent is not None:
							myParent = myParent.pObj
							if myParent is not None:
								mc.select(str(myParent))
							
					if "CHANNELS" in line:
						chan = line.strip().split(" ")
						
						for i in range(2, int(chan[1]) ):
							self._channels.append("%s.%s" % (str(myParent), translationDict[chan[i]] ) )
						
					if "OFFSET" in line:
						offset = line.strip().split(" ")
						print offset
						jnt = pm.joint(name=str(myParent), p=(0,0,0))
						jnt.translate.set([float(offset[1]), float(offset[2]), float(offset[3])])
					
					if myParent is not None:
						print "parent: %s" % str(myParent.pObj)
					
					if "MOTION" in line:
						motion = True
				else:
					if "Frame" not in line:
						data = line.split(" ")
						print "animating.."
						
						for x in range(0, len(data) - 1 ):
							print self._channels
							print data
							print "Set Attribute: %s %f" % (self._channels[x], float(data[x]))
							mc.setAttr(self._channels[x], float(data[x]))
		
	def _on_select_root(self, e):
		selection = pm.ls(sl=True)
		if len(selection) == 0:
			return
		self._rootNode = selection[0]
		mc.textField(self._textfield, e=True, text=str(self._rootNode))
		
if __name__ == "__main__":
	dialog = BVHImporterDialog()
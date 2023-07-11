# 
# BVH Importer script for Maya.
# 
# Importer for .bvh files (BioVision Hierachy files).
# BVH is a common ascii motion capture data format containing skeletal and
# motion data.
# 
# <license>
# BVH Importer script for Maya.
# Copyright (C) 2023  Jeroen Hoolmans
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
import os
import re
from typing import Optional

import maya.cmds as mc

space_re = re.compile(r"\s+")

# This maps the BVH naming convention to Maya
translationDict = {
    "Xposition": "translateX",
    "Yposition": "translateY",
    "Zposition": "translateZ",
    "Xrotation": "rotateX",
    "Yrotation": "rotateY",
    "Zrotation": "rotateZ"
}


class TinyDAG(object):
    """
    Tiny DAG class for storing the hierarchy of the BVH file.
    """

    def __init__(self, obj: str, parent: Optional["TinyDAG"] = None):
        """Constructor"""
        self.obj = obj
        self.__parent = parent

    @property
    def parent(self):
        """Returns the parent of the object"""
        return self.__parent

    def __str__(self) -> str:
        """String representation of the object"""
        return str(self.obj)

    def full_path(self) -> str:
        """Returns the full path of the object"""
        if self.parent is not None:
            return "%s|%s" % (self.parent.full_path(), str(self))
        return str(self.obj)


class BVHImporterDialog(object):
    """
    BVH Importer Dialog

    This class is the main dialog for the BVH importer.
    """

    def __init__(self, debug=False):
        self._name = "bvhImportDialog"
        self._title = "BVH Importer v2.0"

        if debug:
            print("Debug is deprecated.")

        # UI related
        self._textfield = ""
        self._scale_field = ""
        self._frame_field = ""
        self._rotation_order = ""
        self._reload = ""

        # Other
        self._root_node = None  # Used for targeting

        # BVH specific stuff
        self._filename = ""
        self._channels = []

        self.setup_ui()

    def setup_ui(self):
        """
        Builds the UI
        """
        win = self._name
        if mc.window(win, ex=True):
            mc.deleteUI(win)

        # Non sizeable dialog
        win = mc.window(self._name, title=self._title, w=200, rtf=True,
                        sizeable=False)

        mc.columnLayout(adj=1, rs=5)
        mc.separator()
        mc.text("Options")
        mc.separator()

        mc.rowColumnLayout(numberOfColumns=2,
                           columnWidth=[(1, 80), (2, 150)],
                           cal=[(1, "right"), (2, "center")],
                           cs=[(1, 5), (2, 5)],
                           rs=[(1, 5), (2, 5)])

        mc.text("Rig scale")
        self._scale_field = mc.floatField(minValue=0.01, maxValue=2, value=1)
        mc.text("Frame offset")
        self._frame_field = mc.intField(minValue=0)
        mc.text("Rotation Order")
        self._rotation_order = mc.optionMenu()
        mc.menuItem(label='XYZ')
        mc.menuItem(label='YZX')
        mc.menuItem(label='ZXY')
        mc.menuItem(label='XZY')
        mc.menuItem(label='YXZ')
        mc.menuItem(label='ZYX')

        mc.setParent("..")
        mc.separator()

        # Targeting UI
        mc.text("Skeleton Targeting")
        mc.text("(Select the hips)")
        mc.separator()

        mc.rowColumnLayout(numberOfColumns=2,
                           columnWidth=[(1, 150), (2, 80)],
                           cs=[(1, 5), (2, 5)],
                           rs=[(1, 5), (2, 5)])

        self._textfield = mc.textField(editable=False)
        mc.button("Select/Clear", c=self._on_select_root)

        mc.setParent("..")
        mc.separator()
        mc.button("Import..", c=self._on_select_file)
        self._reload = mc.button("Reload", enable=False, c=self._read_bvh)

        # Footer
        mc.text("by Jeroen Hoolmans")

        mc.window(win, e=True, rtf=True, sizeable=False)
        mc.showWindow(win)

    def _on_select_file(self, e):
        """
        Callback for the import button.
        """
        file_filter = "All Files (*.*);;Motion Capture (*.bvh)"
        result = mc.fileDialog2(fileFilter=file_filter, dialogStyle=1, fm=1)

        if result is None or not len(result):
            return

        self._filename = result[0]

        mc.button(self._reload, e=True, enable=True)

        # Action!
        self._read_bvh()

    def load_bvh(self, filename):
        self._filename = filename
        self._read_bvh()

    def _read_bvh(self, *_args):
        # Safe close is needed for End Site part to keep from setting new
        # parent.
        safe_close = False
        # Once motion is active, animate.
        motion = False
        # Clear channels before appending
        self._channels = []

        # Scale the entire rig and animation
        rig_scale = mc.floatField(self._scale_field, q=True, value=True)
        frame = mc.intField(self._frame_field, q=True, value=True)
        rot_order = mc.optionMenu(self._rotation_order, q=True, select=True) - 1

        with open(self._filename) as f:
            # Check to see if the file is valid (sort of)
            if not f.readline().startswith("HIERARCHY"):
                mc.error("No valid .bvh file selected.")
                return False

            if self._root_node is None:
                # Create a group for the rig, easier to scale.
                # (Freeze transform when ungrouping please..)
                mocap_name = os.path.basename(self._filename)
                grp = mc.group(em=True, name="_mocap_%s_grp" % mocap_name)
                mc.setAttr("%s.scale" % grp, rig_scale, rig_scale, rig_scale)

                # The group is now the 'root'
                my_parent = TinyDAG(grp, None)
            else:
                my_parent = TinyDAG(self._root_node, None)
                self._clear_animation()

            for line in f:
                line = line.replace("	", " ")  # force spaces
                if not motion:
                    # root joint
                    if line.startswith("ROOT"):
                        # Set the Hip joint as root
                        if self._root_node:
                            my_parent = TinyDAG(str(self._root_node), None)
                        else:
                            my_parent = TinyDAG(line[5:].rstrip(), my_parent)
                            # Update root node in case we want to reload.
                            self._root_node = my_parent
                            mc.textField(self._textfield,
                                         e=True,
                                         text=my_parent.full_path())

                    if "JOINT" in line:
                        jnt = space_re.split(line.strip())
                        # Create the joint
                        my_parent = TinyDAG(jnt[1], my_parent)

                    if "End Site" in line:
                        # Finish up a hierarchy and ignore a closing bracket
                        safe_close = True

                    if "}" in line:
                        # Ignore when safeClose is on
                        if safe_close:
                            safe_close = False
                            continue

                        # Go up one level
                        if my_parent is not None:
                            my_parent = my_parent.parent
                            if my_parent is not None:
                                mc.select(my_parent.full_path())

                    if "CHANNELS" in line:
                        chan = line.strip()
                        chan = space_re.split(chan)

                        # Append the channels that are animated
                        for i in range(int(chan[1])):
                            self._channels.append("%s.%s" % (
                                my_parent.full_path(),
                                translationDict[chan[2 + i]]
                            ))

                    if "OFFSET" in line:
                        offset = line.strip()
                        offset = space_re.split(offset)
                        jnt_name = str(my_parent)

                        # When End Site is reached, name it "_tip"
                        if safe_close:
                            jnt_name += "_tip"

                        # skip if exists
                        if mc.objExists(my_parent.full_path()):
                            jnt = my_parent.full_path()
                        else:
                            # Build a new joint
                            jnt = mc.joint(name=jnt_name, p=(0, 0, 0))

                        mc.setAttr(jnt + ".rotateOrder", rot_order)
                        mc.setAttr(
                            jnt + ".translate",
                            float(offset[1]),
                            float(offset[2]),
                            float(offset[3])
                        )

                    if "MOTION" in line:
                        # Animate!
                        motion = True

                else:
                    # We don't really need to use Frame count and time
                    # (since Python handles file reads nicely)
                    if "Frame" not in line:
                        data = space_re.split(line.strip())
                        # Set the values to channels
                        for index, value in enumerate(data):
                            mc.setKeyframe(self._channels[index],
                                           time=frame,
                                           value=float(value))

                        frame = frame + 1

    def _clear_animation(self):
        if self._root_node is None:
            mc.error("Could not find root node to clear animation.")
            return

        # Select hierarchy
        mc.select(str(self._root_node), hi=True)
        nodes = mc.ls(sl=True)

        trans_attrs = ["translateX", "translateY", "translateZ"]
        rot_attrs = ["rotateX", "rotateY", "rotateZ"]
        for node in nodes:
            for attr in trans_attrs + rot_attrs:
                # Delete input connections
                connections = mc.listConnections("%s.%s" % (node, attr),
                                                 s=True,
                                                 d=False)
                if connections is not None:
                    mc.delete(connections)

            for attr in rot_attrs:
                # Reset rotation
                mc.setAttr("%s.%s" % (node, attr), 0)

    def _on_select_root(self, *_args):
        # When targeting, set the root joint (Hips)
        selection = mc.ls(sl=True, type="joint", l=True)
        if len(selection) == 0:
            self._root_node = None
            mc.textField(self._textfield, e=True, text="")
        else:
            self._root_node = selection[0]
            mc.textField(self._textfield, e=True, text=self._root_node)


if __name__ == "__main__":
    dialog = BVHImporterDialog()

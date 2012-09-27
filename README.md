BVH Importer Script
===================
By [Jeroen Hoolmans](http://github.com/jhoolmans)

License
-------
BVH Importer script for Maya.
Copyright (C) 2012  Jeroen Hoolmans

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Introduction
------------
When working with motion capture data you may come across .bvh files. These files are BioVision Hierarchy files (http://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html) that hold skeletal information and frame by frame animation.

This script is used to directly import the .bvh files and create a joint structure when needed. No need to load this file inside of MotionBuilder or equivalent and export it to a Maya supported format like FBX.

Installation
------------
Since this is a python script you can easily run the script from a python tab inside the script editor. But if you are frequently using this script I recommand installing the script in the Maya scripts folder.

Windows:

`C:\Users\<username>\Documents\maya\<version>\scripts\`

Mac OSX:

`/Users/Shared/Autodesk/maya/<version>/scripts/`

Linux:

`/home/<username>/maya/<version>/scripts/`

When the script is in place, launch or restart Maya. 
Go to your script editor, open a Python tab and run the following code:

	import bvh_importer
	bvh_importer.BVHImporterDialog()

Enjoy!


Contribution
------------
Helping me develop this script even further is highly appreciated! 

Some ways of contributing:

- Report any bugs by going to [Issues](https://github.com/jhoolmans/mayaImporterBVH/issues).
- Request features at [Issues](https://github.com/jhoolmans/mayaImporterBVH/issues), click 'New Issue' then add the label 'feature request'.

Developers can Fork this repo at [GitHub](https://github.com/jhoolmans/mayaImporterBVH)

- Create a new branch called 'feature name'.
- Make your changes. 
- Do a Pull Request and get some coffee!

Contact
-------
Any questions related to this script can also be posted at [Issues](https://github.com/jhoolmans/mayaImporterBVH/issues). I will get to you as soon as possible!
#!/usr/bin/env python
#    Minceraft-launcher is a fast launcher for minecraft
#    Copyright (C) 2022  Cdr_Johannsen, Muslimitmilch
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys

with open('/usr/share/applications/minceraft.desktop','w') as f:
	f.writelines('[Desktop Entry]\n')
	f.writelines('Name=Minceraft\n')
	f.writelines('StartupWMClass=Minceraft\n')
	f.writelines('Exec=gnome-terminal -t Minceraft --geometry=105x42 -- '+os.path.dirname(os.path.abspath(__file__))+'/minceraft.py\n')
	f.writelines('Icon='+os.path.dirname(os.path.abspath(__file__))+'/minceraft-icon.png\n')
	f.writelines('Type=Application\n')
	f.writelines('Categories=Games;\n')
	f.writelines('Keywords=Minceraft, Python, Quick, Fast, Minecraft;\n')

print('Installed sucsessfully!')
print('You might need to install modules "msmcauth", "readchar", "minecraft_launcher_lib"')

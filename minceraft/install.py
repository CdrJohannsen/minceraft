#!/usr/bin/env python3
#-*- coding:utf-8 -*-
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
import sys, getpass, shutil

user = os.path.expanduser('~')
currDir = os.path.dirname(os.path.abspath(__file__))
sudo = getpass.getpass(f'[sudo] password for {os.getlogin()}:')
print()

####create files
with open('minceraft.desktop','w') as f:
	f.writelines('[Desktop Entry]\n')
	f.writelines('Name=Minceraft\n')
	f.writelines('StartupWMClass=Minceraft\n')
	f.writelines('Exec=gnome-terminal -t Minceraft --geometry=105x42 -- '+user+'/.minceraft/minceraft/minceraft.py\n')
	f.writelines('Icon='+user+'/.minceraft/minceraft/minceraft-icon.png\n')
	f.writelines('Type=Application\n')
	f.writelines('Categories=Games;\n')
	f.writelines('Keywords=Minceraft, Python, Quick, Fast, Minecraft;\n')

with open('minceraft','w') as f:
    f.writelines(['#!/usr/bin/env bash\n'+user+'/.minceraft/minceraft/'+'minceraft.py'])


####create directorys
try:
    os.mkdir(user+'/.minceraft')
    print('creating ~/.minceraft\n')
except:
    print('~/.minceraft was already created')
try:
    os.mkdir(user+'/.minceraft/minceraft')
    print('creating ~/.minceraft/minceraft\n')
except:
    print('~/.minceraft/minceraft was already created')

####move code to ~/.minceraft/minceraft
shutil.copy(currDir+'/azure.json',user+'/.minceraft/minceraft/'+'azure.json')
shutil.copy(currDir+'/encryption.py',user+'/.minceraft/minceraft/'+'encryption.py')
shutil.copy(currDir+'/logo.txt',user+'/.minceraft/minceraft/'+'logo.txt')
shutil.copy(currDir+'/mc_edit.py',user+'/.minceraft/minceraft/'+'mc_edit.py')
shutil.copy(currDir+'/mc_launch.py',user+'/.minceraft/minceraft/'+'mc_launch.py')
shutil.copy(currDir+'/minceraft.py',user+'/.minceraft/minceraft/'+'minceraft.py')
shutil.copy(currDir+'/minceraft-icon.png',user+'/.minceraft/minceraft/'+'minceraft-icon.png')
shutil.copy(currDir+'/terminalDisplay.py',user+'/.minceraft/minceraft/'+'terminalDisplay.py')

####install modules
print('Installing dependencies...\n')
os.system('pip install msmcauth minecraft-launcher-lib')

####move special files
mvDesktop = 'mv '+currDir+'/minceraft.desktop /usr/share/applications/minceraft.desktop'
os.system('echo %s|sudo --prompt='' -S %s' % (sudo, mvDesktop))

os.system('chmod +x '+currDir+'/minceraft')
mvBin = 'mv '+currDir+'/minceraft /usr/bin/minceraft'
os.system('echo %s|sudo --prompt='' -S %s' % (sudo, mvBin))

print('\nFinished Instalation !')

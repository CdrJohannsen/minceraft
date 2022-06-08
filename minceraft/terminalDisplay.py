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

import os, math, json

class advancedDisplay():

    def __init__(self):
        self.outputList = []
        self.homeListFinal = ['', '', '']
        self.logo = True
        self.longSpacer = '                                                                                                                                                                                  '
        self.big_spacer = ''
    
    def getDelay(self, user):
        with open(os.path.expanduser('~')+'/.config/minceraft/preferences.json','r') as f:
            d = json.load(f)
        self.delay = d[user]['delay']
    
    def clear(self):
        self.outputList = []
        self.homeList = []
        os.system('clear')
        
    def listSet(self, appendObject):
        if(type(appendObject) is str):
            self.outputList = [appendObject]
        else:
            self.outputList = appendObject
        self.output()
        
    def listAppend(self, appendObject):
        if(type(appendObject) is str):
            self.outputList += [appendObject]
        else:
            self.outputList += appendObject
        self.output()
    
    def listAppendTop(self, appendObject):
        self.outputList.reverse()
        if(type(appendObject) is str):
            self.outputList += [appendObject]
        else:
            self.outputList += appendObject
        self.outputList.reverse()
        self.output()
    
    def getScreenSize(self):
        screen = os.popen("xrandr -q -d :0").readlines()[0]
        width = screen.split()[7]
        height = screen.split()[9][:-1]
        return width, height
    
    def homeSet(self, homeObject, homeLength = 1):
        self.homeList = []
        if(type(homeObject) is str):
            self.homeList += [homeObject]
        else:
            self.homeList += homeObject
        spacer = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.homeListFinal = [''] + spacer[:max(0, homeLength - len(self.homeList))] + self.homeList + ['']
        self.output()

    def output(self):
        terminalWidth, terminalLength = os.get_terminal_size(0)
        '''
        logoLines = ["    __  ____                            ______ ",
"   /  |/  (_)___  ________  _________ _/ __/ /_",
"  / /|_/ / / __ \/ ___/ _ \/ ___/ __ `/ /_/ __/",
" / /  / / / / / / /__/  __/ /  / /_/ / __/ /_  ",
"/_/  /_/_/_/ /_/\___/\___/_/   \____/_/  \__/  "]
        '''
        with open(os.path.dirname(os.path.abspath(__file__))+'/logo.txt','r') as logo:
            logoLines = logo.read().split('\n')
        os.system('clear')
        if(terminalLength > (len(self.homeListFinal) + len(self.outputList) + len(logoLines) + (terminalLength / 2))):
            for i in range(math.ceil(terminalLength/2) - len(logoLines) - 1):
                print()
            spacer = self.longSpacer[:math.floor((terminalWidth - 48) / 2)]
            for i in logoLines:
                print(spacer, i)
            for i in range(math.floor(terminalLength / 2) - len(self.outputList) - len(self.homeListFinal)):
                print()
        else:
            for i in range(terminalLength - len(self.homeListFinal) - len(self.outputList) - 1):
                print()
        for i in self.outputList:
            print('    ' + i)
        for i in self.homeListFinal:
            print('    ' + i)
            
    def userInput(self):
        return input('      ')

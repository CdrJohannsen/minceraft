import os, math

class terminalDisplay:
	
    def __init__(self):
        self.outputList = []
        self.logo = True
        self.longSpacer = "                                                                                                                                                                                                                              "
		
    def __del__(self):
        pass
        #os.system('clear')
	
    def clear(self):
        pass # selection for debugging purposeseses
        #os.system('clear')
			
    def set(self, input):
        if type(input) is str:
            self.outputList = [input]
        else:
            self.outputList = input
        self.display()
			
    def appendTop(self, lineString):
        self.outputList.reverse()
        self.outputList.append(lineString)
        self.outputList.reverse()
        self.display()	
		
    def append(self, appendObject):
        if(type(appendObject) is str):
            self.outputList.append(appendObject)
        else:
            self.outputList += appendObject
        self.display()
        
	
    def userInput(self):
        return input('    ')
        
    def display(self):
        if(self.logo):
            terminalWidth, terminalLength = os.get_terminal_size(0)
            terminalLength -= 1
            #logoFile = open('logo.txt', 'r')
            logoLines = ["    __  ____                            ______ ",
"   /  |/  (_)___  ________  _________ _/ __/ /_",
"  / /|_/ / / __ \/ ___/ _ \/ ___/ __ `/ /_/ __/",
" / /  / / / / / / /__/  __/ /  / /_/ / __/ /_  ",
"/_/  /_/_/_/ /_/\___/\___/_/   \____/_/  \__/  "] #logoFile.readlines()
            #logoFile.close()
            self.clear()
            if(0 > (terminalLength - (math.ceil(terminalLength / 2)) - len(logoLines) - len(self.outputList))):
                for i in range(terminalLength - len(self.outputList)):
                    print()
            else:
                self.spacerString = self.longSpacer[:int((terminalWidth - 48) / 2)]
                for i in range (math.ceil(terminalLength / 2) - len(logoLines)):
                    print()
                for i in logoLines:
                    print((self.spacerString + i)[:-1])
                for i in range(math.floor(terminalLength / 2) - len(self.outputList)):
                    print()
            for i in self.outputList:
                print('    ' + i)

		
		
		
		
		
class advancedDisplay():

    def __init__(self):
				self.homeLength = 5
        self.outputList = []
        self.homeList = []
        self.logo = True
        self.longSpacer = '                                                                                                                                                                                  '
    
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
        
    def homeSet(self, homeObject, homeLength = 5):
        self.homeLength = homeLength
        self.homeList = ['']
        if(type(homeObject) is str):
            self.homeList += [homeObject]
        else:
            self.homeList += homeObject
        self.homeList.append('')
        self.homeList.reverse()
        self.output()

    def output(self):
        terminalWidth, terminalLength = os.get_terminal_size(0)  
        logoLines = ["    __  ____                            ______ ",
"   /  |/  (_)___  ________  _________ _/ __/ /_",
"  / /|_/ / / __ \/ ___/ _ \/ ___/ __ `/ /_/ __/",
" / /  / / / / / / /__/  __/ /  / /_/ / __/ /_  ",
"/_/  /_/_/_/ /_/\___/\___/_/   \____/_/  \__/  "]
        os.system('clear')
        if(terminalLength > (self.homeLength + len(self.outputList) + len(logoLines) + (terminalLength / 2))):
            for i in range(math.ceil(terminalLength/2) - len(logoLines)):
                print()
            spacer = self.longSpacer[:math.floor((terminalWidth - 48) / 2)]
            for i in logoLines:
                print(spacer, i)
            for i in range(math.floor(terminalLength / 2) - len(self.outputList) - self.homeLength):
                print()
        else:
            for i in range(terminalLength - self.homeLength - len(self.outputList)):
                print()
        for i in self.outputList:
            print('   ' + i)
	self.homeList.reverse()
        while(True):
            if(len(self.homeList) < homeLength):
                self.homeList.append('')
            else:
                break
        self.homeList.reverse()
        for i in self.homeList:
            print('    ' + i)
            
    def userInput(self):
        return input('      ')

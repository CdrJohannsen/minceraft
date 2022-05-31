import time, sys, threading, pickle, os, hashlib, time, math, subprocess, msmcauth
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import mclaunch
import mcedit


###############################################################


def hashValue(inputString):
	hash = hashlib.new('sha256')
	encodedString = inputString.encode()
	hash.update(encodedString)
	return(hash.hexdigest())


def returnNewUser():
    userDic = {}
    display.append("please choose a username")
    userDic["username"] = display.userInput()
    display.append("please choose a password")
    userPassword = display.userInput()
    userDic["passwordHash"] = hashValue(userPassword)
    while(True):
        display.append("please enter your microsoft email adress")
        userDic["msEmail"] = ec.encrypt(display.userInput(), userPassword)
        display.append("please enter your microsoft email password")
        userDic["msPassword"] = ec.encrypt(display.userInput(), userPassword)
        try:
            msEmail = ec.decrypt(userDic["msEmail"], userPassword)
            msPassword = ec.decrypt(userDic["msPassword"], userPassword)
            resp = msmcauth.login(msEmail, msPassword)
            token=resp.access_token
            username=resp.username
            uuid=resp.uuid
            break
        except:
            display.set(['not a correct microsoft account', 'please try again'])
    return(userDic)


def createDirectory():
    display.set(['not found valid config file or directory', 'creating new config directory'])
    try:
        os.mkdir(os.path.join(homePath, ".config/minceraft"))
    except:
        display.set(['could not create directory', 'press ENTER to exit'])


def login():
    homePath = os.path.expanduser('~')
    configPath = os.path.join(homePath, ".config/minceraft/users.bin")
    try:
        configFile = open(configPath, "rb")
        configFileList = pickle.load(configFile)
        configFile.close()
    except:
        display.set(['not found valid config file', 'creating new config file and user'])
        configFileList = [returnNewUser()]
        createDirectory()
        configFile = open(configPath, "wb")
        pickle.dump(configFileList, configFile)
        configFile.close()


    else:
        userSelection = ['[0]    create new user']
        print('DEBUG', configFileList)
        for i in range(len(configFileList)):
            userSelection.append('[' + str(i + 1) + ']    ' + configFileList[i]["username"])
        display.set(userSelection + ['', 'please choose your user profile'])
        while(True):
            userSelected = int(display.userInput())
            if(userSelected == 0):
                display.set('creating new user')
                configFile = open(configPath, "rb")
                configList = pickle.load(configFile)
                configList.append(returnNewUser())
                configFile.close()
                configFile = open(configPath, "wb")
                pickle.dump(configList, configFile)
                configFile.close()
                break
            try:
                userDic = configFileList[userSelected - 1]
                display.set('please enter your password for user ' + userDic['username'])
                while(True):
                    userPassword = display.userInput()
                    if(hashValue(userPassword) == userDic['passwordHash']):
                        break
                    else:
                        display.set('not correct, try again')
                break
            except:
                display.set(userSelection + ['', 'not a valid user, please choose another option'])
		    
    display.set("you successfully logged in")
    return(userDic, userPassword)


'''
def simpleLaunch(email, password):
    minecraft_directory = '/home/malte/.config/minceraft'
    display.append('installing minecraft')
    minecraft_launcher_lib.install.install_minecraft_version("1.8.9", minecraft_directory)
    display.append('finished installing minecraft')
    resp = msmcauth.login(email, password)
    launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": resp.access_token}
    launchOptions["jvmArguments"] = ["-Xmx4G", "-Xms2G"]
    launchCommand = minecraft_launcher_lib.command.get_minecraft_command("1.8.9", minecraft_directory, launchOptions)
    finalLaunchCommand = ''
    for i in launchCommand:
        finalLaunchCommand += ' ' + i
    os.system(finalLaunchCommand)
'''

   

###############################################################


display = terminalDisplay.terminalDisplay()
createDirectory()
os.system('cd .config/minceraft/')
userDic, userPassword = login()


display.set(['', 'select an option'])
display.appendTop('[2]    enter the text editor mode')
display.appendTop('[1]    enter the launch menu')
display.appendTop('[0]    exit minceraft')
while(True):
	userInput = display.userInput()
	
    if(userInput = '0'):
        break
    elif(userInput = '1'):
        pass
    elif(userInput = '2'):
        mcedit.startEditor()
    elif(userInput = '')
        pass
        #open preferences file and do the thing
        #userInput = preferencesDic['mainMenuSelection']
    else:
        display.set(['', 'not a valid option, select another option'])
        display.appendTop('[2]    enter the text editor mode')
        display.appendTop('[1]    enter the launch menu')
        display.appendTop('[0]    exit minceraft')
		
del display

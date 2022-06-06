import time, sys, threading, pickle, os, hashlib, math, subprocess, msmcauth
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import mc_launch
import mc_edit
import readchar
import getpass


###############################################################


def hashValue(inputString):
    hash = hashlib.new('sha256')
    encodedString = inputString.encode()
    hash.update(encodedString)
    return(hash.hexdigest())


def returnNewUser():
    newUserDic = {}
    display.homeSet("please choose a username",1)
    newUserDic["username"] = display.userInput()
    display.homeSet("please choose a password",1)
    userPassword = getpass.getpass('    ')
    newUserDic["passwordHash"] = hashValue(userPassword)
    while True:
        display.homeSet("Select your microsoft authentcation",1)
        display.listSet('[0]  normal (email & password)')
        display.listAppend('[1]  two factor (only for weirdos)')
        auth_type = readchar.readchar()
        if auth_type == '0':
            return normalAuth()
            
        elif auth_type == '1':
            return twoFactorAuth()
            
        else:
            display.homeSet("Not an Option",1)
            time.sleep(2)

def normalAuth():
    while(True):
        display.homeSet("please enter your microsoft email adress",1)
        newUserDic["msEmail"] = ec.encrypt(display.userInput(), userPassword)
        display.homeSet("please enter your microsoft email password",1)
        newUserDic["msPassword"] = ec.encrypt(getpass.getpass('    '), userPassword)
        try:
            msEmail = ec.decrypt(newUserDic["msEmail"], userPassword)
            msPassword = ec.decrypt(newUserDic["msPassword"], userPassword)
            resp = msmcauth.login(msEmail, msPassword)
            launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
            newUserDic['launchOptions']=launchOptions
            break
        except:
            display.listSet(['not a correct microsoft account', 'please try again',e])
    return newUserDic

def twoFactorAuth():
    print('hi')

def createDirectory():
    display.listSet(['not found valid config file or directory', 'creating new config directory'])
    try:
        os.mkdir(os.path.join(homePath, ".minceraft"))
        os.mkdir(os.path.join(homePath, ".config/minceraft"))
        os.mkdir(os.path.join(homePath, ".config/minceraft",'gameDirs'))
    except:
        display.homeSet(['could not create directory', 'press ENTER to exit'])


def login():
    configPath = os.path.join(homePath, ".config/minceraft/users.bin")
    versionsPath = os.path.join(homePath, ".config/minceraft/versions.bin")
    prefsPath = os.path.join(homePath, ".config/minceraft/preferences.bin")
    userDic={}
    userPassword = ''
    userSelected= 0
    try:
        with open(configPath, "rb") as configFile:
            configFileList = pickle.load(configFile)

    except:
        display.listSet(['Not found valid config file', 'Creating new config file and user'])
        configFileList = [returnNewUser()]
        createDirectory()

        with open(configPath, "wb") as configFile:
            pickle.dump(configFileList, configFile)

    try:
        with open(versionsPath, "rb") as versionFile:
            versionFileList = pickle.load(versionFile)
    except:
        versionFileList = [[]]
        with open(versionsPath, "wb") as versionFile:
            pickle.dump(versionFileList, versionFile)
    
    try:
        with open(prefsPath, "rb") as prefFile:
            preferences = pickle.load(prefFile)
    except:
        preferences = [{'last_user':-1}]
        preferences.append({})
        preferences[len(configFileList)]['last_time']=0
        preferences[len(configFileList)]['versions']=[]
        with open(prefsPath, "wb") as prefFile:
            pickle.dump(preferences, prefFile)


    finally:
        print('[DEBUG] ', configFileList)
        loginCorrect = True
        while(True):
            userSelection = ['[0]    create new user']
            for i in range(len(configFileList)):
                userSelection.append('[' + str(i + 1) + ']    ' + configFileList[i]["username"])
                display.listSet(userSelection)
                display.homeSet('please choose your user profile',1)
            if preferences[0]['last_user'] != -1 and loginCorrect:
                userDic = configFileList[int(preferences[0]['last_user'])]
                userSelected = int(preferences[0]['last_user'])+1
            else:
                userSelected = readchar.readchar()
                try:
                    userSelected = int(userSelected)
                    userDic = configFileList[userSelected - 1]
                    if(userSelected == 0):
                        display.listSet('creating new user')
                        with open(configPath, "rb") as configFile:
                            configList = pickle.load(configFile)
                        newUser = returnNewUser()
                        configList.append(newUser)
                        with open(configPath, "wb") as configFile:
                            pickle.dump(configList, configFile)

                        with open(versionPath, "rb") as versionFile:
                            versionFileList = pickle.load(versionFile)
                        versionFileList.append([])
                        with open(versionPath, "wb") as versionFile:
                            pickle.dump(versionFileList, versionFile)
                        
                        with open(prefsPath, "rb") as prefFile:
                            preferences = pickle.load(prefFile)
                        preferences.append({})
                        preferences[0]['last_user'] = len(configList)-1
                        preferences[len(configList)]['last_time']=0
                        preferences[len(configList)]['versions']=[]
                        with open(prefsPath, "wb") as prefFile:
                            pickle.dump(preferences, prefFile)
                        userDic = configFileList[userSelected - 1]
                        break
                except:
                    if userSelected == '\r':
                        if preferences[0]['last_user'] != -1:
                            userDic = configFileList[int(preferences[0]['last_user'])]
                            userSelected = int(preferences[0]['last_user'])+1
            try:
                    display.listSet('')
                    display.homeSet('please enter your password for user ' + userDic['username'],1)
                    while(True):
                            userPassword = getpass.getpass()
                            loginCorrect = False
                            if(hashValue(userPassword) == userDic['passwordHash']):
                                preferences[0]['last_user'] = userSelected-1
                                loginCorrect = True
                                break
                            elif userPassword == '':
                                loginCorrect = False
                                break
                            else:
                                display.homeSet('Not correct, try again',1)
                    if loginCorrect:
                        break
            except:
                    display.listSet(userSelection)
                    display.homeSet('not a valid user, please choose another option',1)
          
    display.homeSet("you successfully logged in")
    with open(prefsPath, "wb") as prefFile:
        pickle.dump(preferences, prefFile)
    return(userDic, userPassword, userSelected-1)


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

homePath = os.path.expanduser('~')
display = terminalDisplay.advancedDisplay()
os.system('cd .config/minceraft/')
CurrentUserDic, userPassword, userSelected = login()
mc_launch.mc_launch(display,userPassword,userSelected)

'''
while(True):
    display.homeSet('Select an option',1)
    display.listSet('[2]    enter the text editor mode')
    display.listAppendTop('[1]    enter the launch menu')
    display.listAppendTop('[0]    exit minceraft')
    userInput = readchar.readchar()

    if(userInput == '0'):
            display.clear()
            break
    elif userInput == '1' or userInput == '\r':
        mc_launch.mc_launch(display,userPassword,userSelected)
    elif userInput == '2':
        mcedit.startEditor()
    elif userInput == '\r':
        pass
        #open preferences file and do the thing
        #userInput = preferencesDic['mainMenuSelection']
        '''
del display

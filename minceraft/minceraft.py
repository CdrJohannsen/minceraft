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

import time, sys, threading, json, os, hashlib, math, subprocess, msmcauth
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import mc_launch
import mc_edit
import readchar
import getpass
import webbrowser

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
        display.homeSet("Select your microsoft authentication",1)
        display.listSet('[0]  normal (email & password)')
        display.listAppend('[1]  two factor (only for weirdos)')
        auth_type = readchar.readchar()
        if auth_type == '0':
            return newNormalAuth(userPassword,newUserDic)
            
        elif auth_type == '1':
            return newTwoFactorAuth(userPassword,newUserDic)
            
        else:
            display.homeSet("Not an Option",1)
            time.sleep(2)

def newNormalAuth(userPassword,newUserDic):
    while(True):
        display.listSet('Normal authentication')
        display.homeSet("please enter your microsoft email adress",1)
        newUserDic["msEmail"] = ec.encrypt(display.userInput(), userPassword)
        display.homeSet("please enter your microsoft email password",1)
        newUserDic["msPassword"] = ec.encrypt(getpass.getpass('    '), userPassword)
        try:
            msEmail = ec.decrypt(newUserDic["msEmail"], userPassword)
            msPassword = ec.decrypt(newUserDic["msPassword"], userPassword)
            display.homeSet("Verifying...",1)
            resp = msmcauth.login(msEmail, msPassword)
            launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
            newUserDic['launchOptions']=launchOptions
            newUserDic['authType'] = 'normal'
            break
        except:
            display.listSet(['not a correct microsoft account', 'please try again'])
    return newUserDic

def newTwoFactorAuth(userPassword,newUserDic):
    while True:
        with open(os.path.dirname(os.path.abspath(__file__))+'/azure.json','r') as f:
            azure = json.load(f)
        client_id = azure['client_id']
        client_secret = azure['client_secret']
        redirect_uri = azure['redirect_uri']
        
        display.homeSet('Please press ENTER and copy the url you will be redirectet to below')
        display.userInput()
        webbrowser.open(minecraft_launcher_lib.microsoft_account.get_login_url(client_id, redirect_uri))
        code_url = display.userInput()
        
        if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(code_url):
            display.homeSet("The url is not valid")
            time.sleep(2)
        else:
            auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(code_url)
            login_data = minecraft_launcher_lib.microsoft_account.complete_login(client_id, secret, redirect_uri, auth_code)
            launchOptions = {"username": login_data['name'], "uuid": login_data['id'], "token": ec.encrypt(login_data['access_token'], userPassword)}
            newUserDic['launchOptions']=launchOptions
            newUserDic['authType'] = '2fa'
            newUserDic['refresh_token'] = ec.encrypt(login_data['refresh_token'], userPassword)

def createDirectory():
    display.listSet(['not found valid config file or directory', 'creating new config directory'])
    try:
        os.mkdir(os.path.join(homePath, ".minceraft"))
    except:
        pass
    try:
        os.mkdir(os.path.join(homePath, ".config/minceraft"))
    except:
        pass
    try:
        os.mkdir(os.path.join(homePath, ".minceraft",'gameDirs'))
    except:
        pass
    try:
        os.mkdir(os.path.join(homePath, ".minceraft",'skins'))
    except:
        pass


def login():
    configPath = os.path.join(homePath, ".config/minceraft/users.json")
    versionsPath = os.path.join(homePath, ".config/minceraft/versions.json")
    prefsPath = os.path.join(homePath, ".config/minceraft/preferences.json")
    userDic={}
    userPassword = ''
    userSelected= 0
    try:
        with open(configPath, "r") as configFile:
            configFileList = json.load(configFile)

    except:
        display.listSet(['Not found valid config file', 'Creating new config file and user'])
        configFileList = [returnNewUser()]
        createDirectory()

        with open(configPath, "w") as configFile:
            json.dump(configFileList, configFile,indent=4)

    try:
        with open(versionsPath, "r") as versionFile:
            versionFileList = json.load(versionFile)
    except:
        versionFileList = [[]]
        with open(versionsPath, "w") as versionFile:
            json.dump(versionFileList, versionFile,indent=4)
    
    try:
        with open(prefsPath, "r") as prefFile:
            preferences = json.load(prefFile)
    except:
        preferences = [{'last_user':-1}]
        preferences.append({})
        preferences[len(configFileList)]['last_time']=time.time()
        preferences[len(configFileList)]['delay']=2
        preferences[len(configFileList)]['versions']=[]
        with open(prefsPath, "w") as prefFile:
            json.dump(preferences, prefFile,indent=4)


    finally:
        print('[DEBUG] ', configFileList)
        loginCorrect = True
        while(True):
            with open(configPath, "r") as configFile:
                configFileList = json.load(configFile)
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
                if userSelected == 'd':
                    display.debug('this message should never appear')
                    display.debug_mode = True
                    display.debug('debug mode is now ON')
                try:
                    userSelected = int(userSelected)
                    userDic = configFileList[userSelected - 1]
                    if(userSelected == 0):
                        display.listSet('creating new user')
                        with open(configPath, "r") as configFile:
                            configList = json.load(configFile)
                        newUser = returnNewUser()
                        configList.append(newUser)
                        with open(configPath, "w") as configFile:
                            json.dump(configList, configFile,indent=4)

                        with open(versionsPath, "r") as versionFile:
                            versionFileList = json.load(versionFile)
                        versionFileList.append([])
                        with open(versionsPath, "w") as versionFile:
                            json.dump(versionFileList, versionFile,indent=4)
                        
                        with open(prefsPath, "r") as prefFile:
                            preferences = json.load(prefFile)
                        preferences.append({})
                        preferences[0]['last_user'] = len(configList)-1
                        preferences[len(configList)]['last_time']=time.time()
                        preferences[len(configList)]['versions']=[]
                        with open(prefsPath, "w") as prefFile:
                            json.dump(preferences, prefFile,indent=4)
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
    with open(prefsPath, "w") as prefFile:
        json.dump(preferences, prefFile,indent=4)
    return(userDic, userPassword, userSelected-1)


   

###############################################################

global debug
homePath = os.path.expanduser('~')
display = terminalDisplay.advancedDisplay()
os.system('cd .config/minceraft/')
CurrentUserDic, userPassword, userSelected = login()
mc_launch.mc_launch(display,userPassword,userSelected)

del display

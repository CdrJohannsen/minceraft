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

import time, os, msmcauth,json
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import subprocess
import mc_edit
import base64
import requests

def mc_launch(dspl,passwd,usr):
    global homePath
    homePath = os.path.expanduser('~')
    global userPassword
    userPassword = passwd
    global userDic
    with open(homePath+'/.config/minceraft/users.json','r') as f:
        userDic = json.load(f)
    global versionList
    with open(homePath+'/.config/minceraft/versions.json','r') as f:
        versionList = json.load(f)
    global preferences
    with open(homePath+'/.config/minceraft/preferences.json','r') as f:
        preferences = json.load(f)
    global display
    display = dspl
    global userSelected
    userSelected = usr
    global minecraft_dir
    minecraft_dir = homePath+'/.minceraft'
    temp_usr = userSelected+1
    display.getDelay(temp_usr)
    while True:
        if selectOption(display):
            return

#########################################################
#Select option
#########################################################

def selectOption(display):
    display.homeSet('Select Option',1)
    display.listSet([userDic[userSelected]['username'],'-------------------------------------'])
    display.listAppend('[i]  install version')
    display.listAppend('[r]  reauthenticate')
    display.listAppend('[d]  delete version')
    display.listAppend('[p]  manage preferences')
    display.listAppend('[s]  change skin')
    display.listAppend('[e]  text editor')
    display.listAppend('[q]  quit')
    i=0
    for v in list(versionList[userSelected]):
        version = str(v[0])
        display.listAppend('['+str(i)+']  '+version)
        i+=1

    selected = display.userInput()
    if selected == 'i':
        install()
        return False

    elif selected == 'r':
        auth()
        return False

    elif selected == 'e':
        mc_edit.startEditor(display)
        return False

    elif selected == 'p':
        managePrefs()
        return False
        
    elif selected == 's':
        manageSkins()
        return False

    if selected == 'q':
        return True
        
    elif selected == 'd':
        deleteVersion()
        return False

    elif selected == '':
        try:
            version = preferences[userSelected+1]['last_played'][0]
            index = preferences[userSelected+1]['last_played'][1]
            launch(version, index)
            return True
        except:
            display.homeSet('No version played last!',1)
            time.sleep(display.delay)
        return False
    else:
        try:
            selected = int(selected)
            try:
                launch(versionList[userSelected][selected][1],selected)
                return True
            except Exception as e:
                display.homeSet('Couldn\'t launch '+versionList[userSelected][selected][1]+'because: '+str(e),1)
                time.sleep(display.delay)
        except:
            display.homeSet('Option not avaliable!',1)
            time.sleep(display.delay)

#########################################################
#Delete a version
#########################################################

def deleteVersion():
    display.homeSet('Select version to delete',1)
    display.listSet('[q]  quit')
    i = 0
    for version in versionList[userSelected]:
        display.listAppend('['+str(i)+']  '+versionList[userSelected][i][0])
        i += 1
    userInput = display.userInput()
    if userInput != 'q':
        try:
            delInput = int(userInput)
            del_version = versionList[userSelected][delInput][1]

            del preferences[userSelected+1]['versions'][delInput]


            if preferences[userSelected+1]['last_played'][0] == del_version:
                preferences[userSelected+1]['last_played'] = ['',-1]
            del versionList[userSelected][delInput]
            with open(homePath+'/.config/minceraft/versions.json', "w") as versionFile:
                json.dump(versionList, versionFile,indent=4)
            with open(homePath+'/.config/minceraft/preferences.json', "w") as prefFile:
                json.dump(preferences, prefFile,indent=4)
        except:
            display.homeSet('Invalid selection!')

#########################################################
#Install
#########################################################

def install():
    versionPath=os.path.join(minecraft_dir,'versions') 
    display.clear()
    display.homeSet(['Select Version','For manual install paste name of directory'],2)
    version = display.userInput()
    display.homeSet('',0)
    display.homeSet('Select Modloader',1)
    display.listSet('[0]  vanilla')
    display.listAppend('[1]  fabric')
    display.listAppend('[2]  forge')
    display.listAppend('[3]  manual install')
    mod = display.userInput()
    display.clear()
    display.homeSet(['Default is version','Select Name'],2)
    name = display.userInput()

    current_max = 390
    callback = {
      "setStatus": set_status,
      "setProgress": set_progress,
      "setMax": set_max
    }
    try:
        success = False
        display.clear()
        display.homeSet('')

        if mod == '0' or mod == '':
            try:
                minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)
                success = True
                new_version = version
            except:
                display.homeSet('Version not avaliable!')


        elif mod == '1':
            try:
                minecraft_launcher_lib.fabric.install_fabric(version, minecraft_dir, callback=callback)
                success=True
                new_version = 'fabric-loader-'+minecraft_launcher_lib.fabric.get_latest_loader_version()+'-'+version
            except:
                display.homeSet('Version not supportet by fabric!',1)
                time.sleep(display.delay)

        ########################  Forge is not working
        elif mod == '2':
            forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
            if forge_version is None and not minecraft_launcher_lib.forge.supports_automatic_install(forge_version):
                display.homeSet("This Minecraft Version is not supported by Forge",1)
                time.sleep(display.delay)
            elif minecraft_launcher_lib.forge.supports_automatic_install(version):
                minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_dir, callback=callback)
                success=True
            else:
                minecraft_launcher_lib.forge.run_forge_installer(forge_version)
                success=True
            dirs = []
            for d in os.listdir(versionPath):
                if os.path.isdir(os.path.join(versionPath,d)):
                    dirs.append(d)
            new_version = sorted(dirs, key=lambda x: os.path.getctime(os.path.join(versionPath,x)), reverse=True)[:1][0]
                
        elif mod == '3':
            display.homeSet('make sure there is a "natives" directory in your versions directory')
            display.userInput()
            success = True
            new_version = version
            
        ############################
        else:
            display.homeSet('Selection not valid!',1)
            time.sleep(display.delay)
        if name == '':
            name = new_version
        if success:   
            try:
                os.mkdir(os.path.join(minecraft_dir,'gameDirs',new_version))
            except:
                display.homeSet('Couldn\'t make game directory',1)
                time.sleep(display.delay)
                    
            try:
                versionList[userSelected].append([name,new_version])
                with open(homePath+'/.config/minceraft/versions.json', "w") as versionFile:
                    json.dump(versionList, versionFile,indent=4)
            except:
                display.homeSet('Couldn\'t save version',1)
                time.sleep(display.delay)
            try:
                preferences[userSelected+1]['versions'].append(getDefaultPrefs(new_version))
                with open(homePath+'/.config/minceraft/preferences.json','w') as f:
                    json.dump(preferences,f,indent=4)
            except:
                display.homeSet('Couldn\'t save preferences',1)
                time.sleep(display.delay)
            
            display.homeSet('Download finished!',1)
    except:
        display.homeSet('Couldn\'t install version',1)
    time.sleep(display.delay)
        
    
    
    
def set_status(status: str):
      global stat
      temp_stat = "{:<25}".format(status)
      stat = temp_stat[:25]


def set_progress(progress: int):
    prog = f"{progress}/{current_max}"
    size = int(os.get_terminal_size()[0])
    barsize = size-len(prog)-len(str(current_max))-2-4-30
    barlen = int(((float(barsize)/(float(current_max)/10))*(progress/10)))
    bar='  ['
    for i in range(barlen):
        bar = bar+'■'
    for i in range(barsize-barlen):
        bar = bar+' '
    bar = bar
    out = '('+prog+')'+((11-len(prog))*' ')+stat+bar
    final = out+(size-len(out)-1)*' '+']'
    print(final+'\r', end='')

    


def set_max(new_max: int):
      global current_max
      current_max = new_max

#########################################################
#Authenticate
#########################################################

def auth():
    if userDic[userSelected]['authType'] == 'normal':
        display.debug('Doing normal auth')
        if not normalAuth():
            return
    elif userDic[userSelected]['authType'] == '2fa':
        display.debug('Doing 2fa auth')
        if not twoFactorAuth():
            return
    else:
        display.homeSet('Couldn\'t authenticate because something weird happened…')
        time.sleep(display.delay)
        
    preferences[userSelected+1]['last_time']=time.time()
    with open(homePath+'/.config/minceraft/users.json','w') as f:
        json.dump(userDic,f,indent=4)
    with open(homePath+'/.config/minceraft/preferences.json','w') as f:
        json.dump(preferences,f,indent=4)


def normalAuth():
    try:
        display.homeSet('Authenticating...',1)
        email = ec.decrypt(userDic[userSelected]['msEmail'], userPassword)
        msPassword = ec.decrypt(userDic[userSelected]["msPassword"], userPassword)
        resp = msmcauth.login(email, msPassword)
        launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
        userDic[userSelected]['launchOptions'] = launchOptions
        return True
    except Exception as e:
        display.homeSet('Authentification failed because of: '+str(e),1)
        time.sleep(display.delay)
        return False


def twoFactorAuth():
    try:
        refresh_token = ec.decrypt(userDic[userSelected]['refresh_token'], userPassword)
        login_data = minecraft_launcher_lib.microsoft_account.complete_refresh(client_id, client_secret, redirect_uri, refresh_token)
        launchOptions = {"username": login_data['name'], "uuid": login_data['id'], "token": ec.encrypt(login_data['access_token'], userPassword)}
        userDic[userSelected]['launchOptions'] = launchOptions
        userDic[userSelected]['refresh_token'] = ec.encrypt(login_data['refresh_token'], userPassword)
        return True
    except Exception as e:
        display.homeSet('Authentification failed because of: '+str(e),1)
        time.sleep(display.delay)
        return False
    
def authIfNeeded():
    try:
        last_time = preferences[userSelected+1]['last_time']
        display.debug('User has played')
    except:
        last_time = preferences[userSelected+1]['last_time'] = 0
        display.debug('User has never played')
    if last_time+42069 <= time.time():
        display.debug('Doing auth with time difference of:'+str(time.time()-last_time))
        auth()
    else:
        display.debug('Doing no auth with time difference of:'+str(time.time()-last_time))

#########################################################
#Launch
#########################################################

def launch(version, index):
    authIfNeeded()
    launchOptions = dict(userDic[userSelected]['launchOptions'])
    game_dir = os.path.join(minecraft_dir,'gameDirs',version)
    launchOptions["gameDirectory"] = game_dir
    access_token = launchOptions['token']
    launchOptions['token']=ec.decrypt(access_token,userPassword)
    launchOptions['launcherName']='minceraft-launcher'
    launchOptions['launcherVersion']='1.1'
    
    launchOptions['customResolution']=True
    screen = display.getScreenSize()
    launchOptions['resolutionWidth']=screen[0]
    launchOptions['resolutionHeight']=screen[1]
    

    version_prefs = preferences[userSelected+1]['versions'][index]
    launchOptions['jvmArguments'] = version_prefs['RAM']
    if version_prefs['server'] != '':
        launchOptions['server'] = version_prefs['server']
        if version_prefs['port'] != '':
            launchOptions['port'] = version_prefs['port']

    
    
    launchCommand = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_dir, launchOptions)
    finalLaunchCommand = ''
    for i in launchCommand:
        finalLaunchCommand += ' ' + i
    if not display.debug_mode:
        nohup = 'nohup '
    else:
        nohup = ''
    finalLaunchCommand = 'cd '+game_dir+' && '+nohup+finalLaunchCommand.replace('--clientId ${clientid} --xuid ${auth_xuid} ','').replace('--userType mojang','--userType msa')+' >/dev/null 2>&1 &'
    finalLaunchCommand = finalLaunchCommand.replace('-DFabricMcEmu= net.minecraft.client.main.Main  ','')#I don't know why this is there, it needs to go for fabric to launch properly
    os.system(finalLaunchCommand)
    preferences[userSelected+1]['last_played']=[version,index]
    with open(homePath+'/.config/minceraft/users.json','w') as f:
        json.dump(userDic,f,indent=4)
    with open(homePath+'/.config/minceraft/preferences.json','w') as f:
            json.dump(preferences,f,indent=4)
    display.homeSet('Starting '+version,1)
    display.debug(finalLaunchCommand)
    time.sleep(3)

#########################################################
#Manage your preferences
#########################################################

def managePrefs():
    while True:
        while True:
            display.listSet([userDic[userSelected]['username'],'-------------------------------------'])
            display.homeSet('Select option to modify',1)
            display.listAppend('[q] quit')
            display.listAppend('[d] manage delay for messages\t\t\tCurrent: '+str(preferences[userSelected+1]['delay']))
            i=0
            for v in list(versionList[userSelected]):
                version = str(v[0])
                display.listAppend('['+str(i)+']  '+version)
                i+=1
            userInput = display.userInput()
            if userInput == 'd':
                manageDelay()
                break
            if userInput == 'q':
                return
            try:
                userInput = int(userInput)
                version_to_change = versionList[userSelected][userInput][1]
            except:
                display.homeSet('Not a valid Option')
                time.sleep(display.delay)
                break
                
            b = 0
            pref_index = (-2)
            for i in preferences[userSelected+1]['versions']:
                if i['version'] == versionList[userSelected][userInput][1]:
                    pref_index = b
                    break
                b += 1
            
            try:
                version_prefs = preferences[userSelected+1]['versions'][pref_index]
            except:
                preferences[userSelected+1]['versions'].append(getDefaultPrefs(version_to_change))
                version_prefs = preferences[userSelected+1]['versions'][len(preferences[userSelected+1]['versions'])-1]
            while True:
                display.homeSet('Select option to modify',1)
                display.listSet([userDic[userSelected]['username'],'-------------------------------------'])
                if version_prefs['server'] != '':
                    server_prefs = version_prefs['server']
                    if version_prefs['port'] != '':
                        server_prefs += ' on port: '+version_prefs['port']
                else:
                    server_prefs = 'None'
                
                display.listAppend('[q] save & quit')
                display.listAppend('[0] manage RAM allocation\t\t\t\tCurrent: '+version_prefs['RAM'][0]+' '+version_prefs['RAM'][1])
                display.listAppend('[1] manage servers to connect after launching\tCurrent: '+server_prefs)
                #print(preferences)
                action = display.userInput()
                if action == 'q':
                    with open(homePath+'/.config/minceraft/preferences.json','w') as f:
                        json.dump(preferences,f,indent=4)
                    break
                elif action == '0':
                    display.homeSet('Specify max RAM allocation in GB')
                    max_ram = display.userInput()
                    try:
                        max_ram = int(max_ram)
                        display.homeSet('Specify min RAM allocation in GB')
                        min_ram = display.userInput()
                        try:
                            min_ram = int(min_ram)
                            version_prefs['RAM'][0] = '-Xmx'+str(max_ram)+'G'
                            version_prefs['RAM'][1] = '-Xms'+str(min_ram)+'G'
                        except:
                            display.homeSet('Not a number')
                            time.sleep(display.delay)
                    except:
                        display.homeSet('Not a number')
                        time.sleep(display.delay)
                elif action == '1':
                    display.homeSet('Set server ip')
                    ip = display.userInput()
                    display.homeSet('If needed set server port')
                    port = display.userInput()
                    version_prefs['server'] = ip
                    version_prefs['port'] = port

    

def getDefaultPrefs(version_to_change):
    defaultPrefs = {'version':version_to_change, 'RAM':['-Xmx2G', '-Xms2G'], 'server': '', 'port' : ''}
    display.debug('Applied default preferences')
    display.debug(defaultPrefs)
    return defaultPrefs


def manageDelay():
    display.homeSet('Delay in seconds')
    display.listSet('Current: '+str(preferences[userSelected+1]['delay']))
    preferences[userSelected+1]['delay'] = float(display.userInput().replace(',','.'))
    delay = preferences[userSelected+1]['delay']
    with open(homePath+'/.config/minceraft/preferences.json','w') as f:
        json.dump(preferences,f,indent=4)
    display.getDelay((userSelected+1))

#########################################################
#Manage your skins
#########################################################

def manageSkins():
    authIfNeeded()
    while True:
        display.listSet('[q] quit')
        i=0
        for skin in os.listdir(os.path.join(homePath,'.minceraft','skins')):
            display.listAppend('['+str(i)+'] '+skin.replace('.png',''))
            i+=1
        
        display.homeSet('Select option')
        userInput = display.userInput()
        if userInput == 'q':
            return
        else:
            try:
                userInput=int(userInput)
            except:
                display.homeSet('Not a valid option')
                time.sleep(display.delay)
                continue
            display.homeSet('Choose skin width')
            display.listSet('[s] slim')
            display.listAppend('[c] classic')
            width = display.userInput()
            if width == 's':
                skinWidth = 'slim'
            elif width == 'c':
                skinWidth = 'classic'
            else:
                disply.homeSet('Not a valid skin type!')
                time.sleep(disply.delay)
                continue
            filename=os.listdir(os.path.join(homePath,'.minceraft','skins'))[userInput]
            changeSkin(ec.decrypt(userDic[userSelected]['launchOptions']['token'],userPassword),os.path.join(homePath,'.minceraft','skins',filename),skinWidth)





def changeSkin(token,filename,skinWidth):
    auth = "Bearer "+token
    url = 'https://api.minecraftservices.com/minecraft/profile/skins'

    data = {'variant':skinWidth}
    headers = {'Authorization': auth}
    with open(filename, 'rb') as png:
        files= {'file': ('skin.png', png, 'image/png')}
        r = requests.request("POST",url,headers=headers,data=data,files=files)
        display.homeSet(r.reason)
        time.sleep(display.delay)
    display.debug('headers: '+str(headers))
    display.debug('data: '+str(data))

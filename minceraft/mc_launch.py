import time, os, msmcauth, pickle
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import readchar
import subprocess
import mc_edit

def mc_launch(dspl,passwd,usr):
    global homePath
    homePath = os.path.expanduser('~')
    global userPassword
    userPassword = passwd
    global userDic
    with open(homePath+'/.config/minceraft/users.bin','rb') as f:
        userDic = pickle.load(f)
    global versionList
    with open(homePath+'/.config/minceraft/versions.bin','rb') as f:
        versionList = pickle.load(f)
    global preferences
    with open(homePath+'/.config/minceraft/preferences.bin','rb') as f:
        preferences = pickle.load(f)
    global display
    display = dspl
    global userSelected
    userSelected = usr
    global minecraft_dir
    minecraft_dir = homePath+'/.minceraft'
    authIfNeeded()
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
    display.listAppend('[e]  text editor')
    display.listAppend('[q]  quit')
    i=0
    for v in list(versionList[userSelected]):
        version = str(v[0])
        display.listAppend('['+str(i)+']  '+version)
        i+=1

    selected = readchar.readchar()
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
        return

    if selected == 'q':
        return True
        
    elif selected == 'd':
        deleteVersion()
        return False

    elif selected == '\r':
        try:
            version = preferences[userSelected+1]['last_played']
            launch(version)
            return True
        except:
            display.homeSet('No version played last!',1)
            time.sleep(2)
        return False
    else:
        try:
            selected = int(selected)
            try:
                launch(versionList[userSelected][selected][1])
                return True
            except:
                display.homeSet('Couldn\'t launch '+versionList[userSelected][selected][1],1)
                time.sleep(2)
        except:
            display.homeSet('Option not avaliable!',1)
            time.sleep(2)

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
            b = 0
            for i in preferences[userSelected+1]['versions']:
                if i['version'] == del_version:
                    del preferences[userSelected+1]['versions'][b]
                    break
                b += 1

            if preferences[userSelected+1]['last_played'] == del_version:
                preferences[userSelected+1]['last_played'] = ''
            del versionList[userSelected][delInput]
            with open(homePath+'/.config/minceraft/versions.bin', "wb") as versionFile:
                pickle.dump(versionList, versionFile)
            with open(homePath+'/.config/minceraft/preferences.bin', "wb") as prefFile:
                pickle.dump(preferences, prefFile)
        except:
            display.homeSet('Invalid selection!')

#########################################################
#Install
#########################################################

def install():
    display.clear()
    display.homeSet('Select Version',1)
    version = display.userInput()
    display.homeSet('',0)
    display.homeSet('Select Modloader',1)
    display.listSet('[0]  vanilla')
    display.listAppend('[1]  fabric')
    display.listAppend('[2]  forge')
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

        if mod == '0':
            try:
                #display.quickSetOptions()
                minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)
                success = True
                new_version = version
            except:
                display.homeSet('Version not avaliable!')


        elif mod == '1':
            try:
                #display.quickSetOptions()
                minecraft_launcher_lib.fabric.install_fabric(version, minecraft_dir, callback=callback)
                success=True
                new_version = 'fabric-loader-'+minecraft_launcher_lib.fabric.get_latest_loader_version()+'-'+version
            except:
                display.homeSet('Version not supportet by fabric!',1)
                time.sleep(2)

        ########################  Forge is not testet
        elif mod == '2':
            forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
            if forge_version is None:
                display.homeSet("This Minecraft Version is not supported by Forge",1)
            else:
                #display.quickSetOptions()
                minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_dir, callback=callback)
                success=True
        ############################
        else:
            display.homeSet('Selection not valid!',1)
            time.sleep(2)
        if success:
            versionPath=os.path.join(minecraft_dir,'versions')    
            try:
                os.mkdir(os.path.join(minecraft_dir,'gameDirs',new_version))
            except:
                display.homeSet('Couldn\'t make game directory',1)
                time.sleep(2)
                    
            try:
                versionList[userSelected].append([name,new_version])
                with open(homePath+'/.config/minceraft/versions.bin', "wb") as versionFile:
                    pickle.dump(versionList, versionFile)
            except:
                display.homeSet('Couldn\'t save version',1)
                time.sleep(2)
            
            display.homeSet('Download finished!',1)
    except:
        display.homeSet('Couldn\'t install version',1)
    time.sleep(2)
        
    
    
    
def set_status(status: str):
      global stat
      stat = "{:<25}".format(status)


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
    bar = bar+']'
    out = '('+prog+')'+((11-len(prog))*' ')+stat+bar
    final = out+(size-len(out))*' '
    print(final+'\r', end='')

    


def set_max(new_max: int):
      global current_max
      current_max = new_max

#########################################################
#Authenticate
#########################################################

def auth():
    try:
        display.homeSet('Authenticating...',1)
        email = ec.decrypt(userDic[userSelected]['msEmail'], userPassword)
        msPassword = ec.decrypt(userDic[userSelected]["msPassword"], userPassword)
        resp = msmcauth.login(email, msPassword)
        launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
        userDic[userSelected]['launchOptions'] = launchOptions
        preferences[userSelected+1]['last_time']=time.time()
        
        with open(homePath+'/.config/minceraft/users.bin','wb') as f:
            pickle.dump(userDic,f)
        with open(homePath+'/.config/minceraft/preferences.bin','wb') as f:
            pickle.dump(preferences,f)
        time.sleep(2)
    except:
        display.homeSet('Authentification failed!',1)
        time.sleep(2)


def authIfNeeded():
    try:
        last_time = preferences[userSelected+1]['last_time']
    except:
        last_time = preferences[userSelected+1]['last_time'] = 0
    if last_time+42069 <= time.time():#42690
        auth()

#########################################################
#Launch
#########################################################

def launch(version):
    launchOptions = dict(userDic[userSelected]['launchOptions'])
    game_dir = os.path.join(minecraft_dir,'gameDirs',version)
    launchOptions["gameDirectory"] = game_dir
    access_token = launchOptions['token']
    launchOptions['token']=ec.decrypt(access_token,userPassword)
    launchOptions['launcherName']='minceraft-launcher'
    launchOptions['launcherVersion']='1.0'
    
    try:
        b = 0
        pref_index = (-2)
        for i in preferences[userSelected+1]['versions']:
            if i['version'] == version:
                pref_index = b
                break
            b += 1
        version_prefs = preferences[userSelected+1]['versions'][pref_index]
        launchOptions['jvmArguments'] = version_prefs['RAM']
        if version_prefs['server'] != '':
            launchOptions['server'] = version_prefs['server']
            if version_prefs['port'] != '':
                launchOptions['port'] = version_prefs['port']
    except:
        pass
    
    
    
    launchCommand = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_dir, launchOptions)
    finalLaunchCommand = ''
    for i in launchCommand:
        finalLaunchCommand += ' ' + i
    finalLaunchCommand = 'cd '+game_dir+' && screen -dm '+finalLaunchCommand.replace('--clientId ${clientid} --xuid ${auth_xuid} ','').replace('--userType mojang','--userType msa')
    finalLaunchCommand = finalLaunchCommand.replace('-DFabricMcEmu= net.minecraft.client.main.Main  ','')#I don't know why this is there, it needs to go for fabric to launch properly
    os.system(finalLaunchCommand)
    preferences[userSelected+1]['last_time']=time.time()
    preferences[userSelected+1]['last_played']=version
    with open(homePath+'/.config/minceraft/users.bin','wb') as f:
        pickle.dump(userDic,f)
    with open(homePath+'/.config/minceraft/preferences.bin','wb') as f:
            pickle.dump(preferences,f)
    display.homeSet('Starting '+version,1)
    #print(finalLaunchCommand)
    time.sleep(3)

#########################################################
#Manage your preferences
#########################################################

def managePrefs():
    display.listSet([userDic[userSelected]['username'],'-------------------------------------'])
    display.homeSet('Select version to modify',1)
    i=0
    for v in list(versionList[userSelected]):
        version = str(v[0])
        display.listAppend('['+str(i)+']  '+version)
        i+=1
    userInput = readchar.readchar()
    try:
        userInput = int(userInput)
        version_to_change = versionList[userSelected][userInput][1]
    except:
        display.homeSet('Not a number')
        time.sleep(2)
        return
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
        
        display.listAppend('[0] save & quit')
        display.listAppend('[1] manage RAM allocation\t\t\t\tCurrent: '+version_prefs['RAM'][0]+' '+version_prefs['RAM'][1])
        display.listAppend('[2] manage servers to connect after launching\tCurrent: '+server_prefs)
        #print(preferences)
        action = readchar.readchar()
        if action == '0':
            with open(homePath+'/.config/minceraft/preferences.bin','wb') as f:
                pickle.dump(preferences,f)
            return
        elif action == '1':
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
                    time.sleep(2)
            except:
                display.homeSet('Not a number')
                time.sleep(2)
        elif action == '2':
            display.homeSet('Set server ip')
            ip = display.userInput()
            display.homeSet('If needed set server port')
            port = display.userInput()
            version_prefs['server'] = ip
            version_prefs['port'] = port

    

def getDefaultPrefs(version_to_change):
    defaultPrefs = {'version':version_to_change, 'RAM':['-Xmx2G', '-Xms2G'], 'server': '', 'port' : ''}
    return defaultPrefs

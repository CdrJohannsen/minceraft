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
    global userSelected
    userSelected = usr
    display = dspl
    global minecraft_dir
    authIfNeeded()
    while True:
        minecraft_dir = homePath+'/.minceraft'
        display.homeSet('Select Option',1)
        display.listSet(userDic[userSelected]['username'])
        display.listAppend('[i]  install version')
        display.listAppend('[r]  reauthenticate')
        display.listAppend('[d]  delete version')
        display.listAppend('[e]  text editor')
        i=0
        for v in list(versionList[userSelected]):
            version = str(v[0])
            display.listAppend('['+str(i)+']  '+version)
            i+=1

        selected = readchar.readchar()
        if selected == 'i':
            install()
        elif selected == 'r':
            auth(userSelected)
        elif selected == 'e':
            mc_edit.startEditor(display)
            
        elif selected == 'd':
            display.homeSet('Select version to delete',1)
            display.listSet('[q]  quit')
            i = 0
            for version in versionList[userSelected]:
                display.listAppend('['+str(i)+']  '+versionList[userSelected][i][0])
                i += 1
            userInput = display.userInput()
            if userInput != 'q':
                try:
                    userInput = int(userInput)
                    del versionList[userSelected][userInput]
                    with open(homePath+'/.config/minceraft/versions.bin', "wb") as versionFile:
                        pickle.dump(versionList, versionFile)
                except:
                    display.homeSet('Invalid selection!')

        elif selected == '\r':
            version = userDic[userSelected]['last_played']['version']
            if version != '':
                launch(userDic[userSelected]['last_played']['version'])
                break
            else:
                display.homeSet('No version played last!',1)
                time.sleep(2)
        else:
            try:
                selected = int(selected)
                try:
                    launch(versionList[userSelected][selected][1])
                    break
                except Exception as e:
                    display.homeSet('Couldn\'t launch '+versionList[userSelected][selected][1],1)
                    print(e)
                    time.sleep(2)
            except:
                display.homeSet('Option not avaliable!',1)
                time.sleep(2)
    quit()


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

        if mod == '0':
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
            except Exception as exe:
                display.homeSet('Version not supportet by fabric!',1)
                print(exe)
                raise exe
                time.sleep(30)

        ########################  Forge is not testet
        elif mod == '2':
            forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
            if forge_version is None:
                display.homeSet("This Minecraft Version is not supported by Forge",1)
            else:
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
                display.homeSet('Couldn\'t rename dir',1)
                time.sleep(2)
                    
            try:
                versionList[userSelected].append([name,new_version])
                with open(homePath+'/.config/minceraft/versions.bin', "wb") as versionFile:
                    pickle.dump(versionList, versionFile)
            except:
                time.sleep(2)
            display.homeSet('Download finished!',1)
    except:
        display.homeSet('Couldn\'t install version',1)
    time.sleep(5)
        
    
    
    
def set_status(status: str):
      display.homeSet(status,1)

def set_progress(progress: int):
    prog = f"{progress}/{current_max}"
    size = int(os.get_terminal_size()[0])
    barsize = size-len(prog)-len(str(current_max))-2-4
    barlen = int(round(((float(barsize)/(float(current_max)/10))*(progress/10)),0))
    bar='   ['
    for i in range(barlen):
        bar = bar+'■'
    for i in range(barsize-barlen):
        bar = bar+' '
    bar = bar+']'
    print('\r'+bar+prog,end='\r')
    


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
    except:
        display.homeSet('Authentification failed!',1)
        time.sleep(2)


def authIfNeeded():
    if preferences[userSelected+1]['last_time']+82800 < time.time():
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
    launchCommand = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_dir, launchOptions)
    finalLaunchCommand = ''
    for i in launchCommand:
        finalLaunchCommand += ' ' + i
    finalLaunchCommand = 'cd '+game_dir+' && screen -dm '+finalLaunchCommand.replace('--clientId ${clientid} --xuid ${auth_xuid} ','')
    finalLaunchCommand = finalLaunchCommand.replace('-DFabricMcEmu= net.minecraft.client.main.Main  ','')#I don't know why this is there, it needs to go for fabric to launch
    os.system(finalLaunchCommand)
    preferences[userSelected+1]['last_time']=time.time()
    userDic[userSelected]['last_played']['version']=version
    with open(homePath+'/.config/minceraft/users.bin','wb') as f:
        pickle.dump(userDic,f)
    with open(homePath+'/.config/minceraft/preferences.bin','wb') as f:
            pickle.dump(preferences,f)
    display.homeSet('Starting '+version,1)
    #print(finalLaunchCommand)
    time.sleep(3)

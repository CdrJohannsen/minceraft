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

import time, json, os, msmcauth
import minecraft_launcher_lib
import encryption
import optionHandler
import argparse
import requests
import webbrowser

###############################################################


def addUser(oh:optionHandler.OptionHandler, user_info):
    oh.config.append(user_info)
    oh.updateUsers()
    oh.user = len(oh.users)
    oh.updateUserInfo()
    oh.updateUsername()
    oh.saveConfig()

def newNormalAuth(oh,username,password,email,ms_password) -> bool:
    try:
        resp = msmcauth.login(email, ms_password)
        launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": encryption.encrypt(resp.access_token, password)}
        user_info = {
            "username":username,
            "passwordHash":encryption.hashValue(password),
            "msEmail": encryption.encrypt(email,password),
            "msPassword": encryption.encrypt(ms_password,password),
            "authType": "normal",
            "last_time": time.time(),
            "launchOptions": launchOptions,
            "last_played": -1,
            "versions":[]
        }
        addUser(oh,user_info)
        return True
    except:
        return False

def twoFactorOpenBrowser():
    with open(os.path.dirname(os.path.abspath(__file__))+'/azure.json','r') as f:
        azure = json.load(f)
    client_id = azure['client_id']
    redirect_uri = azure['redirect_uri']
    webbrowser.open(minecraft_launcher_lib.microsoft_account.get_login_url(client_id, redirect_uri))
    return

def newTwoFactorAuth(oh,username,password,url):
    if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url):
        return False
    else:
        with open(os.path.dirname(os.path.abspath(__file__))+'/azure.json','r') as f:
            azure = json.load(f)
        client_id = azure['client_id']
        redirect_uri = azure['redirect_uri']
        auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url)
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(client_id,client_secret = None, redirect_uri=redirect_uri, auth_code=auth_code)
        launchOptions = {"username": login_data['name'], "uuid": login_data['id'], "token": encryption.encrypt(login_data['access_token'], password)}
        user_info = {
            "username":username,
            "passwordHash":encryption.hashValue(password),
            "authType": "2fa",
            "refresh_token": encryption.encrypt(login_data["refresh_token"],password),
            "last_time": time.time(),
            "launchOptions": launchOptions,
            "last_played": -1,
            "versions":[]
        }
        addUser(oh,user_info)
        return True

def deleteVersion(oh:optionHandler.OptionHandler,del_version):
    if oh.user_info["last_played"]==-1:
        pass
    elif del_version == oh.user_info["last_played"]:
        oh.user_info["last_played"]=-1
    elif del_version < oh.user_info["last_played"]:
        oh.user_info["last_played"]-=1
    del oh.versions[del_version]
    oh.saveConfig()

#########################################################
#Install
#########################################################
def is_version_valid(oh:optionHandler.OptionHandler,version,modloader):
    if not minecraft_launcher_lib.utils.is_version_valid(version,oh.minceraftDir):
        return True
    if modloader == 1:
        if not minecraft_launcher_lib.fabric.is_minecraft_version_supported(version):
            return False
    if modloader == 2:
        if not minecraft_launcher_lib.forge.find_forge_version(version):
            return False

def generateVersion(oh:optionHandler.OptionHandler,version,alias,quickPlay):
    version = {
        "version": version,
        "alias": alias,
        "quickPlay": quickPlay,
        "memory": ["2","2"],
        "server": "",
        "port": "",
    }
    oh.versions.append(version)
    oh.saveConfig()

def install(oh: optionHandler.OptionHandler,version,modloader,alias,callback):
    new_version = version
    if modloader == '0' or modloader == '':
        minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraftDir, callback=callback)
        new_version = version

    elif modloader == '1':
        minecraft_launcher_lib.fabric.install_fabric(version, oh.minceraftDir, callback=callback)
        new_version = 'fabric-loader-'+minecraft_launcher_lib.fabric.get_latest_loader_version()+'-'+version

    elif modloader == '2':
        forge_version = minecraft_launcher_lib.forge.find_forge_version(version)

        installed_versions = minecraft_launcher_lib.utils.get_installed_versions(oh.minceraftDir)
        base_version_avaliable = False
        for i in installed_versions:
            if version in i.values():
                base_version_avaliable = True

        if minecraft_launcher_lib.forge.supports_automatic_install(forge_version):
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraftDir, callback=callback)
            minecraft_launcher_lib.forge.install_forge_version(forge_version, oh.minceraftDir, callback=callback)
        else:
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraftDir, callback=callback)
            minecraft_launcher_lib.forge.run_forge_installer(forge_version)
        new_version = forge_version
            
    elif modloader == '3':
        new_version = version
    else:
        oh.debug(f"Invalid modloader selected: {modloader}")
        raise
        
    ############################
    if alias == '':
        alias = new_version
    try:
        os.mkdir(os.path.join(oh.minceraftDir,'gameDirs',alias.replace(" ","-")))
    except:
        oh.debug("Couldn't make gameDirectory")
    generateVersion(oh,new_version,alias,0)
    
    
    
#########################################################
#Authenticate
#########################################################

def auth(oh:optionHandler.OptionHandler):
    if oh.user_info["authType"] == 'normal':
        oh.debug('Doing normal auth')
        if not normalAuth(oh):
            return False
    elif oh.user_info["authType"] == '2fa':
        oh.debug('Doing 2fa auth')
        if not twoFactorAuth(oh):
            return False
    else:
        pass
        
    oh.user_info['last_time']=time.time()
    oh.saveConfig()
    return True

def normalAuth(oh:optionHandler.OptionHandler):
    try:
        email = encryption.decrypt(oh.user_info['msEmail'], oh.password)
        msPassword = encryption.decrypt(oh.user_info["msPassword"], oh.password)
        resp = msmcauth.login(email, msPassword)
        launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": encryption.encrypt(resp.access_token, oh.password)}
        oh.user_info['launchOptions'] = launchOptions
        return True
    except Exception as e:
        oh.debug('Authentification failed because of: '+str(e),1)
        return False


def twoFactorAuth(oh:optionHandler.OptionHandler):
    try:
        with open(os.path.dirname(os.path.abspath(__file__))+'/azure.json','r') as f:
            azure = json.load(f)
        client_id = azure['client_id']
        redirect_uri = azure['redirect_uri']

        refresh_token = encryption.decrypt(oh.user_info['refresh_token'], oh.password)
        login_data = minecraft_launcher_lib.microsoft_account.complete_refresh(client_id, client_secret = None, redirect_uri = redirect_uri, refresh_token = refresh_token)
        launchOptions = {"username": login_data['name'], "uuid": login_data['id'], "token": encryption.encrypt(login_data['access_token'], oh.password)}
        oh.user_info['launchOptions'] = launchOptions
        oh.user_info['refresh_token'] = encryption.encrypt(login_data['refresh_token'], oh.password)
        return True
    except Exception as e:
        oh.debug('Authentification failed because of: '+str(e),1)
        return False
    
def authIfNeeded(oh:optionHandler.OptionHandler):
    last_time = oh.user_info['last_time']
    oh.debug('User has played')
    if last_time+42069 <= time.time():
        oh.debug('Doing auth with time difference of:'+str(time.time()-last_time))
        auth(oh)
    else:
        oh.debug('Doing no auth with time difference of:'+str(time.time()-last_time))

#########################################################
#Launch
#########################################################

def launch(oh:optionHandler.OptionHandler, version_index):
    authIfNeeded(oh)
    oh.debug(version_index)
    launchOptions = dict(oh.user_info['launchOptions'])
    version_prefs = oh.user_info['versions'][version_index]
    game_dir = os.path.join(oh.gameDirs,version_prefs["alias"].replace(" ","-"))
    launchOptions["gameDirectory"] = game_dir
    access_token = launchOptions['token']
    launchOptions['token']=encryption.decrypt(access_token,oh.password)
    launchOptions['launcherName']='minceraft-launcher'
    launchOptions['launcherVersion']=oh.config[0]["launcher_version"]
    launchOptions['jvmArguments'] = [
        f"-Xmx{version_prefs['memory'][0]}G",
        f"-Xms{version_prefs['memory'][1]}G"
    ]
    if version_prefs['server'] != '':
        launchOptions['server'] = version_prefs['server']
        if version_prefs['port'] != '':
            launchOptions['port'] = version_prefs['port']
    if oh.server:
        launchOptions['server'] = oh.server
        if oh.port:
            launchOptions['port'] = str(oh.port)

    launchCommand = minecraft_launcher_lib.command.get_minecraft_command(version_prefs["version"], oh.minceraftDir, launchOptions)
    finalLaunchCommand = ''
    for i in launchCommand:
        finalLaunchCommand += ' ' + i
    if not oh.debug_mode:
        nohup = 'nohup '
        dev_null = ' >/dev/null 2>&1 &'
    else:
        nohup = ''
        dev_null = ''
    finalLaunchCommand = f"cd \"{game_dir}\" && {nohup}{finalLaunchCommand.replace('--clientId ${clientid} --xuid ${auth_xuid} ','').replace('--userType mojang','--userType msa')}{dev_null}"
    finalLaunchCommand = finalLaunchCommand.replace('-DFabricMcEmu= net.minecraft.client.main.Main  ','')#I don't know why this is there, it needs to go for fabric to launch properly
    os.system(finalLaunchCommand)
    oh.user_info['last_played']=version_index
    oh.saveConfig()
    oh.debug(finalLaunchCommand)

#########################################################
#Manage your skins
#########################################################


def listSkins(oh:optionHandler.OptionHandler) -> list:
    return os.listdir(os.path.join(oh.minceraftDir,"skins"))


def changeSkin(oh:optionHandler.OptionHandler,filename,skinWidth):
    authIfNeeded(oh)
    auth = "Bearer "+encryption.decrypt(oh.user_info["launchOptions"]["token"],oh.password)
    url = 'https://api.minecraftservices.com/minecraft/profile/skins'

    data = {'variant':skinWidth}
    headers = {'Authorization': auth}
    with open(filename, 'rb') as png:
        files= {'file': ('skin.png', png, 'image/png')}
        r = requests.request("POST",url,headers=headers,data=data,files=files)
        oh.debug(r.reason)
    oh.debug('headers: '+str(headers))
    oh.debug('data: '+str(data))

def handleArgs(oh):
    argParser = argparse.ArgumentParser(description="A fast launcher for Minecraft")
    argParser.add_argument("-u", "--user", type=str, help="selected user")
    argParser.add_argument("-ui", "--user_index", type=int, help="index of selected user. Has higher priority than -u")
    argParser.add_argument("-lu", "--list_user", action='store_true', help="list users and their indices")
    argParser.add_argument("-p", "--password", type=str,help ="password for user")
    argParser.add_argument("-v", "--version", type=int, help="version to launch")
    argParser.add_argument("-lv", "--list_version", action='store_true', help="list versions and their indices")
    argParser.add_argument("--server", type=str, help="server to connect after booting", metavar="IP/URL")
    argParser.add_argument("--port", type=int, help="port for --server")
    argParser.add_argument("-d", "--debug",action='store_true', help="enable debug mode")
    args = argParser.parse_args()
    oh.from_args(args)

###############################################################

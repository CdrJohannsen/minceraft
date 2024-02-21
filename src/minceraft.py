"""
Main code for the backend

Minceraft-launcher is a fast launcher for minecraft
Copyright (C) 2024  Cdr_Johannsen, Muslimitmilch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import time
import json
import os
import argparse
import webbrowser
import requests

import msmcauth
import minecraft_launcher_lib

import encryption
from optionHandler import OptionHandler

###############################################################

azure_path = os.path.dirname(os.path.abspath(__file__)) + "/azure.json"


def addUser(oh: OptionHandler, user_info: dict):
    """Add a new user account"""
    oh.config.append(user_info)
    oh.updateUsers()
    oh.user = len(oh.users)
    oh.updateUserInfo()
    oh.updateUsername()
    oh.saveConfig()


def newNormalAuth(
    oh: OptionHandler, username: str, password: str, email: str, ms_password: str
) -> bool:
    """Add a new user account with normal authentification"""
    try:
        resp = msmcauth.login(email, ms_password)
        launch_options = {
            "username": resp.username,
            "uuid": resp.uuid,
            "token": encryption.encrypt(resp.access_token, password),
        }
        user_info = {
            "username": username,
            "passwordHash": encryption.hashValue(password),
            "msEmail": encryption.encrypt(email, password),
            "msPassword": encryption.encrypt(ms_password, password),
            "authType": "normal",
            "last_time": time.time(),
            "launch_options": launch_options,
            "last_played": -1,
            "versions": [],
        }
        addUser(oh, user_info)
        return True
    except:  # pylint: disable=bare-except
        return False


def twoFactorOpenBrowser():
    """Open the redirect url in the users browser"""
    with open(azure_path, "r", encoding="utf-8") as f:
        azure = json.load(f)
    client_id = azure["client_id"]
    redirect_uri = azure["redirect_uri"]
    webbrowser.open(
        minecraft_launcher_lib.microsoft_account.get_login_url(client_id, redirect_uri)
    )


def newTwoFactorAuth(oh: OptionHandler, username: str, password: str, url: str):
    """Add a new user account with 2 factor authentification"""
    if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url):
        return False
    with open(azure_path, "r", encoding="utf-8") as f:
        azure = json.load(f)
    client_id = azure["client_id"]
    redirect_uri = azure["redirect_uri"]
    auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url)
    if auth_code is None:
        return False
    login_data = minecraft_launcher_lib.microsoft_account.complete_login(
        client_id,
        client_secret=None,
        redirect_uri=redirect_uri,
        auth_code=auth_code,
    )
    launch_options = {
        "username": login_data["name"],
        "uuid": login_data["id"],
        "token": encryption.encrypt(login_data["access_token"], password),
    }
    user_info = {
        "username": username,
        "passwordHash": encryption.hashValue(password),
        "authType": "2fa",
        "refresh_token": encryption.encrypt(login_data["refresh_token"], password),
        "last_time": time.time(),
        "launch_options": launch_options,
        "last_played": -1,
        "versions": [],
    }
    addUser(oh, user_info)
    return True


def deleteVersion(oh: OptionHandler, del_version: int):
    """Deletes the entry for a version"""
    # Set last played version to a valid value
    if oh.user_info.get("last_played") == -1:
        pass
    elif del_version == oh.user_info.get("last_played"):
        oh.user_info["last_played"] = -1
    elif del_version < oh.user_info.get("last_played"):
        oh.user_info["last_played"] -= 1
    del oh.versions[del_version]
    oh.saveConfig()


#########################################################
# Install
#########################################################
def isVersionValid(oh: OptionHandler, version: str, modloader: str):
    """Check if a version is valid for a given modloader"""
    if not minecraft_launcher_lib.utils.is_version_valid(version, oh.minceraft_dir):
        return True
    if modloader == "1":
        if not minecraft_launcher_lib.fabric.is_minecraft_version_supported(version):
            return False
    if modloader == "2":
        if not minecraft_launcher_lib.forge.find_forge_version(version):
            return False
    return None


def generateVersion(oh: OptionHandler, version: str, alias: str, quick_play: int):
    """Generates a configuration dict for a version"""
    new_version = {
        "version": version,
        "alias": alias,
        "quickPlay": quick_play,
        "memory": ["2", "2"],
        "server": "",
        "port": "",
    }
    oh.versions.append(new_version)
    oh.saveConfig()


def install(
    oh: OptionHandler, version: str, modloader: str, alias: str, callback: dict
):
    """Installs a version
    Args:
        version:    str     The name of the version
        modloader:  str     The selected modloader
                                0 or empty for Vanilla
                                1 for Fabric
                                2 for Forge
                                3 for manual installation
        alias:      str     The name that should be exposed to the user
        callback:   dict    Callback functions for the install progress
    """
    new_version = version
    # Vanilla
    if modloader in ["0", ""]:
        minecraft_launcher_lib.install.install_minecraft_version(
            version, oh.minceraft_dir, callback=callback
        )
        new_version = version

    # Fabric
    elif modloader == "1":
        minecraft_launcher_lib.fabric.install_fabric(
            version, oh.minceraft_dir, callback=callback
        )
        new_version = (
            "fabric-loader-"
            + minecraft_launcher_lib.fabric.get_latest_loader_version()
            + "-"
            + version
        )

    # Forge
    elif modloader == "2":
        forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
        if forge_version is None:
            return

        installed_versions = minecraft_launcher_lib.utils.get_installed_versions(
            oh.minceraft_dir
        )
        base_version_avaliable = False
        for i in installed_versions:
            if version in i.values():
                base_version_avaliable = True

        if minecraft_launcher_lib.forge.supports_automatic_install(forge_version):
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(
                    version, oh.minceraft_dir, callback=callback
                )
            minecraft_launcher_lib.forge.install_forge_version(
                forge_version, oh.minceraft_dir, callback=callback
            )
        else:
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(
                    version, oh.minceraft_dir, callback=callback
                )
            minecraft_launcher_lib.forge.run_forge_installer(forge_version)
        new_version = forge_version

    # Manual
    elif modloader == "3":
        new_version = version
    else:
        oh.debug(f"Invalid modloader selected: {modloader}")
        return

    ############################
    if alias == "":
        alias = new_version
    try:
        os.mkdir(os.path.join(oh.minceraft_dir, "game_dirs", alias.replace(" ", "-")))
    except FileNotFoundError:
        oh.debug("Couldn't make gameDirectory")
    generateVersion(oh, new_version, alias, 0)


#########################################################
# Authenticate
#########################################################


def auth(oh: OptionHandler):
    """Authenticates with the users selected auth method"""
    if oh.user_info["authType"] == "normal":
        oh.debug("Doing normal auth")
        if not normalAuth(oh):
            return False

    elif oh.user_info["authType"] == "2fa":
        oh.debug("Doing 2fa auth")
        if not twoFactorAuth(oh):
            return False
    else:
        pass

    oh.user_info["last_time"] = time.time()
    oh.saveConfig()
    return True


def normalAuth(oh: OptionHandler):
    """Authenticate the normal way"""
    try:
        email = encryption.decrypt(oh.user_info["msEmail"], oh.password)
        ms_password = encryption.decrypt(oh.user_info["msPassword"], oh.password)
        resp = msmcauth.login(email, ms_password)
        launch_options = {
            "username": resp.username,
            "uuid": resp.uuid,
            "token": encryption.encrypt(resp.access_token, oh.password),
        }
        oh.user_info["launch_options"] = launch_options
        return True
    except Exception as e:  # pylint: disable=broad-exception-caught
        oh.debug("Authentification failed because of: " + str(e))
        return False


def twoFactorAuth(oh: OptionHandler):
    """Authenticate with 2fa"""
    try:
        with open(azure_path, "r", encoding="utf-8") as f:
            azure = json.load(f)
        client_id = azure["client_id"]
        redirect_uri = azure["redirect_uri"]

        refresh_token = encryption.decrypt(oh.user_info["refresh_token"], oh.password)
        login_data = minecraft_launcher_lib.microsoft_account.complete_refresh(
            client_id,
            client_secret=None,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token,
        )
        launch_options = {
            "username": login_data["name"],
            "uuid": login_data["id"],
            "token": encryption.encrypt(login_data["access_token"], oh.password),
        }
        oh.user_info["launch_options"] = launch_options
        oh.user_info["refresh_token"] = encryption.encrypt(
            login_data["refresh_token"], oh.password
        )
        return True
    except Exception as e:  # pylint: disable=broad-exception-caught
        oh.debug("Authentification failed because of: " + str(e))
        return False


def authIfNeeded(oh: OptionHandler):
    """Calls the auth() function if the last authentification was at least 42069 seconds ago"""
    last_time = oh.user_info["last_time"]
    oh.debug("User has played")
    if last_time + 42069 <= time.time():
        oh.debug("Doing auth with time difference of:" + str(time.time() - last_time))
        auth(oh)
    else:
        oh.debug(
            "Doing no auth with time difference of:" + str(time.time() - last_time)
        )


#########################################################
# Launch
#########################################################


def launch(oh: OptionHandler, version_index: int):
    """Launches minecraft"""
    authIfNeeded(oh)
    oh.debug(version_index)
    launch_options = dict(oh.user_info["launchOptions"])
    version_prefs = oh.user_info["versions"][version_index]
    game_dir = os.path.join(oh.game_dirs, version_prefs["alias"].replace(" ", "-"))
    launch_options["gameDirectory"] = game_dir
    access_token = launch_options["token"]
    launch_options["token"] = encryption.decrypt(access_token, oh.password)
    launch_options["launcherName"] = "minceraft-launcher"
    launch_options["launcherVersion"] = oh.config[0]["launcher_version"]
    launch_options["jvmArguments"] = [
        f"-Xmx{version_prefs['memory'][0]}G",
        f"-Xms{version_prefs['memory'][1]}G",
    ]
    if version_prefs["server"] != "":
        launch_options["server"] = version_prefs["server"]
        if version_prefs["port"] != "":
            launch_options["port"] = version_prefs["port"]
    if oh.server:
        launch_options["server"] = oh.server
        if oh.port:
            launch_options["port"] = str(oh.port)

    launch_command = minecraft_launcher_lib.command.get_minecraft_command(
        version_prefs["version"], oh.minceraft_dir, launch_options
    )
    final_launch_command = ""
    for i in launch_command:
        final_launch_command += " " + i
    if not oh.debug_mode:
        nohup = "nohup "
        dev_null = " >/dev/null 2>&1 &"
    else:
        nohup = ""
        dev_null = ""
    final_launch_command = f'cd "{game_dir}" && {nohup}{final_launch_command}{dev_null}'
    final_launch_command = final_launch_command.replace(
        "-DFabricMcEmu= net.minecraft.client.main.Main  ",
        "",  # I don't know why this is there, it needs to go for fabric to launch properly
    )
    os.system(final_launch_command)
    oh.user_info["last_played"] = version_index
    oh.saveConfig()
    oh.debug(final_launch_command)


#########################################################
# Manage your skins
#########################################################


def listSkins(oh: OptionHandler) -> list:
    """Returns a list of all skins"""
    return os.listdir(os.path.join(oh.minceraft_dir, "skins"))


def changeSkin(oh: OptionHandler, filename: str, skin_width: str):
    """Change a users skins"""
    authIfNeeded(oh)
    authorization = "Bearer " + encryption.decrypt(
        oh.user_info["launch_options"]["token"], oh.password
    )
    url = "https://api.minecraftservices.com/minecraft/profile/skins"

    data = {"variant": skin_width}
    headers = {"Authorization": authorization}
    with open(filename, "rb") as png:
        files = {"file": ("skin.png", png, "image/png")}
        r = requests.request(
            "POST", url, headers=headers, data=data, files=files, timeout=5
        )
        oh.debug(r.reason)
    oh.debug("headers: " + str(headers))
    oh.debug("data: " + str(data))


def handleArgs(oh: OptionHandler):
    """Handle cli arguments"""
    parser = argparse.ArgumentParser(description="A fast launcher for Minecraft")
    parser.add_argument("-g", "--gui", action="store_true", help="Start minceraft in gui mode")
    parser.add_argument("-u", "--user", type=str, help="selected user")
    parser.add_argument(
        "-ui",
        "--user_index",
        type=int,
        help="index of selected user. Has higher priority than -u",
    )
    parser.add_argument(
        "-lu", "--list_user", action="store_true", help="list users and their indices"
    )
    parser.add_argument("-p", "--password", type=str, help="password for user")
    parser.add_argument("-v", "--version", type=int, help="version to launch")
    parser.add_argument(
        "-lv",
        "--list_version",
        action="store_true",
        help="list versions and their indices",
    )
    parser.add_argument(
        "--server", type=str, help="server to connect after booting", metavar="IP/URL"
    )
    parser.add_argument("--port", type=int, help="port for --server")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()
    oh.fromArgs(args)


###############################################################

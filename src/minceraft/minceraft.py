"""
Main code for the backend

Minceraft-launcher is a fast launcher for minecraft
Copyright (C) 2025  Cdr_Johannsen, Muslimitmilch

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

import argparse
import json
import os
import time
from importlib import metadata

import gi
import minecraft_launcher_lib
import requests

# pylint: disable=wrong-import-position
gi.require_version("GLib", "2.0")
gi.require_version("WebKit", "6.0")
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, WebKit
from minecraft_launcher_lib.types import CallbackDict, MinecraftOptions

from minceraft import encryption
from minceraft.optionHandler import OptionHandler

# pylint: enable=wrong-import-position


###############################################################

azure_path = os.path.dirname(os.path.abspath(__file__)) + "/azure.json"


class LoginApp(Gtk.Application):
    """Creates a window for the user to log into their Microsoft account"""

    def __init__(self, url: str, redirect_uri: str):
        Gtk.Application.__init__(self)
        self.url = url
        self.redirect_uri = redirect_uri

    def onLoadChanged(self, _, _0):
        """Called when the url of the webview changes"""
        if self._view.props.uri.startswith(self.redirect_uri):
            self.url = self._view.props.uri
            self.win.close()
            # pylint: disable=no-value-for-parameter
            if GLib.main_context_default().is_owner():
                GLib.main_context_default().release()
            # pylint: enable=no-value-for-parameter

    def onActivate(self, application):
        """Activates the window"""
        self.win = Gtk.Window(  # pylint: disable=attribute-defined-outside-init
            title="Login to your Microsoft account", width_request=300, height_request=600
        )
        if application is not None:
            self.add_window(self.win)
        self._view = WebKit.WebView.new()  # pylint: disable=attribute-defined-outside-init,no-value-for-parameter
        self._view.connect("load_changed", self.onLoadChanged)
        self.win.set_child(self._view)
        self._view.load_uri(self.url)
        self.win.present()

    def getUrl(self):
        """Returns the saved url"""
        return self.url


def addUser(oh: OptionHandler, user_info: dict):
    """Add a new user account"""
    oh.config.append(user_info)
    oh.updateUsers()
    oh.user = len(oh.users)
    oh.updateUserInfo()
    oh.updateUsername()
    oh.saveConfig()


def newAuth(oh: OptionHandler) -> tuple[dict, str] | tuple[dict, None]:
    """
    Authentificates the user with the microsoft account

    This is only needed once, as all further authentifications will be done with the refresh_token
    """
    with open(azure_path, "r", encoding="utf-8") as f:
        azure = json.load(f)
    client_id = azure["client_id"]
    redirect_uri = azure["redirect_uri"]
    GLib.log_set_writer_func(
        lambda a, b, c: GLib.LogWriterOutput.HANDLED,
    )
    app = LoginApp(minecraft_launcher_lib.microsoft_account.get_login_url(client_id, redirect_uri), redirect_uri)
    app.connect("activate", app.onActivate)
    # pylint: disable=no-value-for-parameter
    # This is incredibly ugly
    if GLib.main_context_default().acquire():
        app.run()
    else:
        GLib.main_context_default().invoke_full(1, app.onActivate, (app, None))
        GLib.main_context_default().iteration(True)
    # pylint: enable=no-value-for-parameter
    url = app.getUrl()
    oh.debug(url)
    if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url):
        return {}, None
    with open(azure_path, "r", encoding="utf-8") as f:
        azure = json.load(f)
    client_id = azure["client_id"]
    redirect_uri = azure["redirect_uri"]
    auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url)
    if auth_code is None:
        return {}, None
    login_data = minecraft_launcher_lib.microsoft_account.complete_login(
        client_id,
        client_secret=None,
        redirect_uri=redirect_uri,
        auth_code=auth_code,
    )
    launch_options = {
        "username": login_data["name"],
        "uuid": login_data["id"],
        "token": encryption.encryptAES(login_data["access_token"], oh.password),
    }
    return launch_options, login_data["refresh_token"]


def newUser(oh: OptionHandler, username: str, password: str) -> bool:
    """Add a new user account"""
    launch_options, refresh_token = newAuth(oh)
    if refresh_token is not None:
        user_info = {
            "username": username,
            "passwordHash": encryption.hashValue(password),
            "refresh_token": encryption.encryptAES(refresh_token, password),
            "last_time": time.time(),
            "launchOptions": launch_options,
            "last_played": -1,
            "versions": [],
        }
        addUser(oh, user_info)
        return True
    return False


def deleteVersion(oh: OptionHandler, del_version: int):
    """Deletes the entry for a version"""
    # Set last played version to a valid value
    if oh.user_info.get("last_played", -1) == -1:
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
def isVersionValid(oh: OptionHandler, version: str, modloader: str) -> bool | None:
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


def install(oh: OptionHandler, version: str, modloader: str, alias: str, callback: CallbackDict):
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
    if modloader in ("0", ""):
        minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraft_dir, callback=callback)
        new_version = version

    # Fabric
    elif modloader == "1":
        minecraft_launcher_lib.fabric.install_fabric(version, oh.minceraft_dir, callback=callback)
        new_version = "fabric-loader-" + minecraft_launcher_lib.fabric.get_latest_loader_version() + "-" + version

    # Forge
    elif modloader == "2":
        forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
        if forge_version is None:
            return

        installed_versions = minecraft_launcher_lib.utils.get_installed_versions(oh.minceraft_dir)
        base_version_avaliable = False
        for i in installed_versions:
            if version in i.values():
                base_version_avaliable = True

        if minecraft_launcher_lib.forge.supports_automatic_install(forge_version):
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraft_dir, callback=callback)
            minecraft_launcher_lib.forge.install_forge_version(forge_version, oh.minceraft_dir, callback=callback)
        else:
            if not base_version_avaliable:
                minecraft_launcher_lib.install.install_minecraft_version(version, oh.minceraft_dir, callback=callback)
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
        os.mkdir(os.path.join(oh.game_dirs, alias.replace(" ", "-")))
    except FileNotFoundError:
        oh.debug(f"Couldn't make gameDirectory, parent directory {oh.minceraft_dir} does not exist")
    except FileExistsError:
        oh.debug("Game directory already exists")
    generateVersion(oh, new_version, alias, 0)


#########################################################
# Authenticate
#########################################################


def auth(oh: OptionHandler) -> bool:
    """Authenticates with the users selected auth method"""
    if "authType" in oh.user_info:
        oh.debug("Redoing the initial auth")
        launch_options, refresh_token = newAuth(oh)
        if refresh_token is None:
            return False
        oh.user_info["refresh_token"] = encryption.encryptAES(refresh_token, oh.password)
        oh.user_info["launchOptions"] = launch_options
        del oh.user_info["authType"]
        if "msEmail" in oh.user_info:
            del oh.user_info["msEmail"]
            del oh.user_info["msPassword"]
    else:
        oh.debug("Authenticating...")
        if not doAuth(oh):
            return False

    oh.user_info["last_time"] = time.time()
    oh.saveConfig()
    return True


def doAuth(oh: OptionHandler) -> bool:
    """Refresh authentification"""
    try:
        with open(azure_path, "r", encoding="utf-8") as f:
            azure = json.load(f)
        client_id = azure["client_id"]
        redirect_uri = azure["redirect_uri"]

        refresh_token = encryption.decryptAES(oh.user_info["refresh_token"], oh.password)
        login_data = minecraft_launcher_lib.microsoft_account.complete_refresh(
            client_id,
            client_secret=None,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token,
        )

        launch_options = {
            "username": login_data["name"],
            "uuid": login_data["id"],
            "token": encryption.encryptAES(login_data["access_token"], oh.password),
        }
        oh.user_info["launchOptions"] = launch_options
        oh.user_info["refresh_token"] = encryption.encryptAES(login_data["refresh_token"], oh.password)
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
        oh.debug("Doing no auth with time difference of:" + str(time.time() - last_time))


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
    launch_options["token"] = encryption.decryptAES(access_token, oh.password)
    launch_options["launcherName"] = "minceraft-launcher"
    launch_options["launcherVersion"] = metadata.version("minceraft")
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
        version_prefs["version"], oh.minceraft_dir, MinecraftOptions(**launch_options)
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
# Manage your skins and capes
#########################################################


def listSkins(oh: OptionHandler) -> list:
    """Returns a list of all skins"""
    return os.listdir(os.path.join(oh.minceraft_dir, "skins"))


def changeSkin(oh: OptionHandler, filename: str, skin_width: str):
    """Change a users skins"""
    authIfNeeded(oh)
    authorization = "Bearer " + encryption.decryptAES(oh.user_info["launchOptions"]["token"], oh.password)
    url = "https://api.minecraftservices.com/minecraft/profile/skins"

    data = {"variant": skin_width}
    headers = {"Authorization": authorization}
    with open(filename, "rb") as png:
        files = {"file": ("skin.png", png, "image/png")}
        r = requests.request("POST", url, headers=headers, data=data, files=files, timeout=5)
        oh.debug(r.reason)
    oh.debug("headers: " + str(headers))
    oh.debug("data: " + str(data))


def listCapes(oh: OptionHandler) -> tuple[list[tuple[str, str]], str | None]:
    """Returns a list of all owned capes"""
    authIfNeeded(oh)
    authorization = "Bearer " + encryption.decryptAES(oh.user_info["launchOptions"]["token"], oh.password)
    url = "https://api.minecraftservices.com/minecraft/profile"
    headers = {"Authorization": authorization}
    r = requests.get(url, headers=headers, timeout=5).json()
    capes = []
    current_cape = None
    for cape in r["capes"]:
        capes.append((cape["alias"], cape["id"]))
        if cape["state"] == "ACTIVE":
            current_cape = cape["alias"]
    return capes, current_cape


def changeCape(oh: OptionHandler, cape: tuple[str, str], current_cape: str | None):
    """Change a users cape"""
    authIfNeeded(oh)
    authorization = "Bearer " + encryption.decryptAES(oh.user_info["launchOptions"]["token"], oh.password)
    url = "https://api.minecraftservices.com/minecraft/profile/capes/active"

    headers = {"Authorization": authorization, "Content-Type": "application/json"}
    if current_cape == cape[0]:
        r = requests.delete(url, headers=headers, timeout=5)
    else:
        data = {"capeId": cape[1]}
        r = requests.put(url, headers=headers, json=data, timeout=5)
        oh.debug("data: " + str(data))
    oh.debug(r.reason)
    oh.debug("headers: " + str(headers))


#########################################################
# Handle CLI arguments
#########################################################


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
    parser.add_argument("-lu", "--list_user", action="store_true", help="list users and their indices")
    parser.add_argument("-p", "--password", type=str, help="password for user")
    parser.add_argument("-v", "--version", type=int, help="version to launch")
    parser.add_argument(
        "-lv",
        "--list_version",
        action="store_true",
        help="list versions and their indices",
    )
    parser.add_argument("--server", type=str, help="server to connect after booting", metavar="IP/URL")
    parser.add_argument("--port", type=int, help="port for --server")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()
    oh.fromArgs(args)


###############################################################

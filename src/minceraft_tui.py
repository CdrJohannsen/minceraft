#!/usr/bin/env python3
"""
A TUI for the minceraft launcher

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

import os
import time

import minceraft
import terminalDisplay

DEFAULT_DELAY = 1


class MinecraftTui:
    """
    TUI Interface for Minceraft
    """

    def __init__(self):
        self.oh = minceraft.OptionHandler()
        minceraft.handleArgs(self.oh)
        self.display = terminalDisplay.AdvancedDisplay(self.oh)
        self.oh.setDebugCallback(self.display.debug)
        self.current_max = 0
        self.install_max = 0
        self.install_status = str()
        if not self.oh.load():
            self.newUser()

    def run(self):
        """
        Starts the TUI Interface
        """

        self.handleAccountSelection()
        self.oh.updateUsers()
        self.oh.updateUserInfo()
        self.oh.updateUsername()
        self.oh.updateVersions()
        self.oh.saveConfig()
        while True:
            if self.selectOption():
                self.oh.saveConfig()
                exit()

    def selectAccount(self):
        """
        Asks the user for their wanted account
        Select 0 for a new account
        """

        users = self.oh.listUsernames()
        user_selection = ["[0]\t\tcreate new user"]
        for i in range(len(users)):
            user_selection.append(f"[{i+1}]\t\t{users[i]}")
        self.display.listSet(user_selection)
        user = self.display.userInput()
        try:
            self.oh.user = int(user)
        except ValueError:
            self.display.homeSet(
                [
                    "Please choose your user profile",
                    f"Must be a number from 0 to {len(users)}",
                ]
            )
            self.selectAccount()
        self.handleAccountSelection()

    def handleAccountSelection(self):
        """
        Handles if a new account should be created or a login should follow
        """

        if self.oh.user == 0:
            self.newUser()
        else:
            self.oh.updateUsername()
            self.oh.updateUserInfo()
            self.display.clear()
            self.login()

    def login(self):
        """
        Asks for the users password if it doesn't already exsist
        If it is empty the user will return to the account selection
        Checks if the password is correct
        """

        if not self.oh.password:
            self.display.homeSet(
                "Please enter your password for user " + self.oh.username, 1
            )
            self.oh.password = self.display.userPassword()
        if self.oh.password == "":
            self.display.homeSet("Please choose your user profile")
            self.selectAccount()
        if self.oh.user_info["passwordHash"] == minceraft.encryption.hashValue(
            self.oh.password
        ):
            self.oh.config[0]["last_user"] = self.oh.user
            return
        self.display.homeSet("Password not correct, try again")
        self.oh.password = self.display.userInput()
        self.login()

    def newUser(self):
        """
        Adds a new User
        """

        self.display.homeSet("Please choose a username")
        username = self.display.userInput()
        password, password2 = "1", "2"  # Set password to random different values
        while password != password2:
            self.display.homeSet("Please choose a password")
            password = self.display.userInput()
            self.display.homeSet("Please repeat the password")
            password2 = self.display.userInput()
        self.display.homeSet("Select your microsoft authentication")
        while True:
            self.display.listSet("[0]  normal (email & password)")
            self.display.listAppend("[1]  two factor (only for weirdos)")
            auth_type = self.display.userInput()
            if auth_type in ["1", "2"]:
                break
            self.display.homeSet(
                ["Option not avaliable", "Select your microsoft authentication type"]
            )
        auth_successfull = False
        while not auth_successfull:
            if auth_type == "0":
                self.display.listSet("Normal authentication")
                self.display.homeSet("please enter your microsoft email adress")
                email = self.display.userInput()
                self.display.homeSet("please enter your microsoft email password")
                ms_password = self.display.userInput()
                self.display.homeSet("Verifying...", 1)
                auth_successfull = minceraft.newNormalAuth(
                    self.oh, username, password, email, ms_password
                )
                if not auth_successfull:
                    self.display.listSet(
                        ["Not a correct microsoft account", "Please try again"]
                    )
                    time.sleep(DEFAULT_DELAY)
            else:
                self.display.listSet("Two factor authentication")
                minceraft.twoFactorOpenBrowser()
                self.display.homeSet(
                    [
                        "Your browser should have opened",
                        "Please paste the url you will be redirected to below",
                    ]
                )
                url = self.display.userInput()
                auth_successfull = minceraft.newTwoFactorAuth(
                    self.oh, username, password, url
                )
                if not auth_successfull:
                    self.display.listSet("The url is not valid, try again")
                    time.sleep(DEFAULT_DELAY)
        self.oh.password = password

    def selectOption(self) -> bool:
        """
        Main menu for the TUI launcher
        Select from many options
        Programm exits if return is True
        """

        if self.oh.version is None:
            self.display.homeSet("Select Option", 1)
            self.display.listSet(
                [self.oh.username, "-------------------------------------"]
            )
            self.display.listAppend("[i]  install version")
            self.display.listAppend("[r]  reauthenticate")
            self.display.listAppend("[d]  delete version")
            self.display.listAppend("[p]  manage preferences")
            self.display.listAppend("[s]  change skin")
            self.display.listAppend("[q]  quit")
            i = 0
            for v in self.oh.versions:
                version = v["alias"]
                self.display.listAppend("[" + str(i) + "]  " + version)
                i += 1
            selected = self.display.userInput()
        else:
            selected = None

        exit_after = False

        match selected:
            case "i":
                self.install()

            case "r":
                self.display.homeSet("Authenticating...", 1)
                if not minceraft.auth(self.oh):
                    self.display.homeSet("Authentication failed")

            case "p":
                self.managePrefs()

            case "s":
                self.manageSkins()

            case "q":
                exit_after = True

            case "d":
                self.deleteVersion()

            case "":
                version_index = self.oh.user_info["last_played"]
                if version_index == -1:
                    self.display.homeSet("No version played last!", 1)
                    time.sleep(DEFAULT_DELAY)
                else:
                    self.launch(version_index)
                    exit_after = True
            case _:
                if self.oh.version is None:
                    try:
                        self.oh.version = int(selected)
                    except ValueError:
                        self.display.homeSet("Option not avaliable!", 1)
                        time.sleep(DEFAULT_DELAY)
                        return exit_after
                if len(self.oh.versions) <= self.oh.version:
                    self.display.homeSet(
                        f"Version with index {self.oh.version} not avaliable", 1
                    )
                    self.oh.version = None
                    time.sleep(DEFAULT_DELAY)
                    return exit_after
                self.launch(self.oh.version)
                exit_after = True
        return exit_after

    def manageSkins(self):
        """
        Menu for changing skin
        """

        while True:
            self.display.listSet("[q] quit")
            skins = minceraft.listSkins(self.oh)
            for i in range(len(skins)):
                self.display.listAppend(f"[{i}] {skins[i].replace('.png','')}")

            self.display.homeSet("Select option")
            index = self.display.userInput()
            if index == "q":
                return
            try:
                index = int(index)
            except ValueError:
                self.display.homeSet("Not a valid option")
                time.sleep(DEFAULT_DELAY)
                continue
            self.display.homeSet("Choose skin width")
            self.display.listSet("[s] slim")
            self.display.listAppend("[c] classic")
            width = self.display.userInput()
            if width == "s":
                skin_width = "slim"
            elif width == "c":
                skin_width = "classic"
            else:
                self.display.homeSet("Not a valid skin type!")
                time.sleep(DEFAULT_DELAY)
                continue
            minceraft.changeSkin(
                self.oh,
                os.path.join(self.oh.minceraft_dir, "skins", skins[index]),
                skin_width,
            )

    def managePrefs(self):
        """
        UI for managing preferences
        """
        while True:
            self.display.listSet(
                [self.oh.username, "-------------------------------------"]
            )
            self.display.homeSet("Select option to modify", 1)
            self.display.listAppend("[q] quit")
            for i in range(len(self.oh.versions)):
                self.display.listAppend(f"[{i}] {self.oh.versions[i]['alias']}")
            user_input = self.display.userInput()
            if user_input == "q":
                return
            try:
                user_input = int(user_input)
            except ValueError:
                self.display.homeSet("Not a valid Option")
                time.sleep(DEFAULT_DELAY)
                continue

            version_prefs = self.oh.versions[user_input]
            while True:
                self.display.homeSet("Select option to modify", 1)
                self.display.listSet(
                    [self.oh.username, "-------------------------------------"]
                )
                if version_prefs["server"] != "":
                    server_prefs = version_prefs["server"]
                    if version_prefs["port"] != "":
                        server_prefs += " on port: " + version_prefs["port"]
                else:
                    server_prefs = "None"

                current_ram_string = f"-Xmx{version_prefs['memory'][0]}G -Xms{version_prefs['memory'][1]}G"

                self.display.listAppend("[q] save & quit")
                self.display.listAppend(
                    f"[0] manage RAM allocation\t\t\t\tCurrent: {current_ram_string}"
                )
                self.display.listAppend(
                    f"[1] manage servers to connect after launching\tCurrent: {server_prefs}"
                )
                action = self.display.userInput()
                if action == "q":
                    self.oh.saveConfig()
                    break
                if action == "0":
                    self.display.homeSet("Specify max RAM allocation in GB")
                    max_ram = self.display.userInput()
                    try:
                        max_ram = int(max_ram)
                        self.display.homeSet("Specify min RAM allocation in GB")
                        min_ram = self.display.userInput()
                        try:
                            min_ram = int(min_ram)
                            version_prefs["memory"][0] = max_ram
                            version_prefs["memory"][1] = min_ram
                        except ValueError:
                            self.display.homeSet("Not a number")
                            time.sleep(DEFAULT_DELAY)
                    except ValueError:
                        self.display.homeSet("Not a number")
                        time.sleep(DEFAULT_DELAY)
                elif action == "1":
                    self.display.homeSet("Set server ip")
                    ip = self.display.userInput()
                    self.display.homeSet("If needed set server port")
                    port = self.display.userInput()
                    version_prefs["server"] = ip
                    version_prefs["port"] = port

    def deleteVersion(self):
        """
        Selects the version to delete and calls minceraft.deleteVersion() for deletion
        """

        self.display.homeSet("Select version to delete", 1)
        self.display.listSet("[q]  quit")
        for i in range(len(self.oh.versions)):
            self.display.listAppend("[" + str(i) + "]  " + self.oh.versions[i]["alias"])
        del_version = self.display.userInput()
        if del_version != "q":
            try:
                del_version = int(del_version)
            except ValueError:
                self.display.homeSet("Must be a number")
                return
            if del_version >= len(self.oh.versions):
                self.display.homeSet(f"Must be between 0 and {len(self.oh.versions)-1}")
            else:
                minceraft.deleteVersion(self.oh, del_version)

    def launch(self, version_index: int):
        """
        Calls the minceraft.launch command and displays the startet version
        """

        self.display.homeSet(
            f"Preparing to launch {self.oh.versions[version_index]['alias']}"
        )
        minceraft.launch(self.oh, version_index)
        self.display.homeSet(f"Starting {self.oh.versions[version_index]['alias']}")
        time.sleep(3)

    def install(self):
        """
        Handles the selection of the version, modloader and alias for the install
        """
        self.display.clear()
        latest = minceraft.minecraft_launcher_lib.utils.get_latest_version()
        self.display.homeSet(
            [
                "Select Version",
                "For manual install paste name of directory",
                f'Latest release: {latest["release"]}  Latest snapshot: {latest["snapshot"]}',
            ]
        )
        version = self.display.userInput()
        self.display.homeSet("")
        self.display.homeSet("Select Modloader")
        self.display.listSet("[0]  vanilla")
        self.display.listAppend("[1]  fabric")
        self.display.listAppend("[2]  forge")
        self.display.listAppend("[3]  manual install")
        modloader: str = self.display.userInput()
        if not modloader in ["", "0", "1", "2", "3"]:
            self.display.homeSet("Not a valid Modloader")
            return
        self.display.clear()
        self.display.homeSet(["Default is version", "Select Name"])
        alias = self.display.userInput()
        self.install_max = 390
        callback = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }
        self.display.clear()
        self.display.homeSet("")
        version_unavaliable = minceraft.isVersionValid(self.oh, version, modloader)
        # True: Vanilla version not avaliable
        # False: Version not supportet by modloader
        # None: Version supportet
        if version_unavaliable:
            self.display.homeSet("Version not avaliable")
        elif version_unavaliable is False:
            if modloader == "1":
                self.display.homeSet("Version not supportet by Fabric")
            elif modloader == "2":
                self.display.homeSet("Version not supportet by Forge")
        else:
            minceraft.install(self.oh, version, modloader, alias, callback)

    def setStatus(self, status: str):
        """
        Set installation status
        Used as a callback function
        """
        temp_stat = f"{status:.25}"
        self.install_status = temp_stat[:25]

    def setProgress(self, progress: int):
        """
        Set installation progress
        Used as a callback function
        """
        prog = f"{progress}/{self.current_max}"
        size = int(os.get_terminal_size()[0])
        barsize = size - len(prog) - len(str(self.current_max)) - 2 - 4 - 30
        barlen = int(
            ((float(barsize) / (float(self.current_max) / 10)) * (progress / 10))
        )
        bar = "  ["
        bar = bar + "■" * barlen
        bar = bar + " " * (barsize - barlen)
        out = "(" + prog + ")" + ((11 - len(prog)) * " ") + self.install_status + bar
        final = out + (size - len(out) - 1) * " " + "]"
        print(final + "\r", end="")

    def setMax(self, new_max: int):
        """
        Set installation maximum progress
        Used as a callback function
        """
        self.current_max = new_max


if __name__ == "__main__":
    mc_tui = MinecraftTui()
    mc_tui.run()

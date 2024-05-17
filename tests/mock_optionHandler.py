"""
Handles all data to be stored

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

import json
import os
import shutil
import tempfile


class MockOptionHandler:
    """
    Handle the options and config
    """

    def __init__(self):
        self.home_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../build")
        self.minceraft_dir = os.path.join(self.home_path, ".minceraft")
        self.versions_dir = os.path.join(self.minceraft_dir, "versions")
        self.game_dirs = os.path.join(self.minceraft_dir, "gameDirs")
        self._config_file = tempfile.NamedTemporaryFile()
        self.config_path = self._config_file.name
        shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config.json"), self.config_path)
        self.config = []
        self.reloadConfig()
        self.password = str()
        self.version = 0
        self.versions = []
        self.user_info = {}
        self.users = []
        self.username = str()
        self.server = None
        self.port = None
        self.debug_mode = False
        self.debug = print
        self.user = 0
        self.user = self.config[0]["last_user"]
        self.updateUsers()

    def load(self) -> bool:
        """Load the config"""
        if len(self.config) == 1:
            return False
        self.updateUsers()
        self.updateUserInfo()
        self.updateUsername()
        self.updateVersions()
        return True

    def updateVersions(self) -> None:
        """Update the version list"""
        self.versions = self.user_info["versions"]

    def updateUsers(self) -> None:
        """Update the user list"""
        self.users = self.config[1:]

    def updateUserInfo(self) -> None:
        """Update the info about the current user"""
        self.user_info = self.config[self.user]

    def updateUsername(self) -> None:
        """Update the username to the current user"""
        self.username = self.config[self.user]["username"]

    def reloadConfig(self) -> None:
        """Reload the config file"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def saveConfig(self) -> None:
        """Save the config to the config file"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def listUsernames(self) -> list:
        """Returns a list of all avaliable users"""
        usernames = []
        for i in self.users:
            usernames.append(i["username"])
        return usernames

    def setDebugCallback(self, callback) -> None:
        """Sets the internal debug callback"""
        self.debug = callback

    def fromArgs(self, args) -> None:
        """Loads the cli arguments"""
        if args.user_index:
            self.user = args.user_index
            if args.user_index > len(self.users):
                print(f"Index must be between 0 and {len(self.users)}")
                exit(1)
        else:
            if args.user in self.listUsernames():
                self.user = self.listUsernames().index(args.user) + 1
            elif args.user is None:
                pass
            else:
                print(f"User {args.user} does not exsist")
                exit(1)
        self.password = args.password
        self.version = args.version
        if self.version is not None:
            self.updateUserInfo()
            self.updateVersions()
            self.version -= 1
            if self.version > len(self.user_info["versions"]) - 1:
                print(f"Index out of range. Version must be between 0 and {len(self.user_info['versions'])-1}")
                exit(1)
        self.server = args.server
        self.port = args.port
        self.debug_mode = args.debug
        if args.list_user:
            self.cliListUsers()
            exit(0)
        if args.list_version:
            self.cliListVersions()
            exit(0)

    def cliListUsers(self) -> None:
        """Print a list of avaliable users to stdout"""
        users = self.listUsernames()
        print("[INDEX]\t\tUSER")
        for i in range(len(users)):
            users[i] = f"[{str(i+1)}]\t\t{users[i]}"
            print(users[i])

    def cliListVersions(self) -> None:
        """Print a list of avaliable versions to stdout"""
        if not self.user:
            print("No user specified")
            exit(1)
        self.updateUserInfo()
        self.updateVersions()
        i = 1
        print("[INDEX]\t\tVERSION")
        for v in self.versions:
            print(f'[{str(i)}]\t\t{v["alias"]}')
            i += 1

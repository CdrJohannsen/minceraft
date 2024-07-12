"""
TUI frontend

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
import math
import time
import getpass


class AdvancedDisplay:
    """
    Draws the TUI
    """

    def __init__(self, oh):
        self.output_list = []
        self.home_list_final = ["", "", ""]
        self.logo = True
        self.long_spacer = " " * 178
        self.big_spacer = ""
        self.home_list = []
        self.delay = 0
        self.oh = oh

    def clear(self):
        """
        Clears the terminal
        """
        self.output_list = []
        self.home_list = []
        print("\x1b[2J")

    def listSet(self, append_object):
        """
        Set the list area to append_object
        """
        if isinstance(append_object, str):
            self.output_list = [append_object]
        else:
            self.output_list = append_object
        self.output()

    def listAppend(self, append_object):
        """
        Append append_object to the list area
        """
        if isinstance(append_object, str):
            self.output_list += [append_object]
        else:
            self.output_list += append_object
        self.output()

    def listPrepend(self, append_object):
        """
        Prepend append_object to the list area
        """
        self.output_list.reverse()
        if isinstance(append_object, str):
            self.output_list += [append_object]
        else:
            self.output_list += append_object
        self.output_list.reverse()
        self.output()

    def homeSet(self, home_object: str | list, home_length: int = 1):
        """
        Set the home area to home_object
        """
        self.home_list = []
        if isinstance(home_object, str):
            self.home_list += [home_object]
        else:
            self.home_list += home_object
        spacer = [""] * 20
        self.home_list_final = (
            [""]
            + spacer[: max(0, home_length - len(self.home_list))]
            + self.home_list
            + [""]
        )
        self.output()

    def output(self):
        """
        Print everything to stdout
        """
        terminal_width, terminal_length = os.get_terminal_size(0)
        with open(
            os.path.dirname(os.path.abspath(__file__)) + "/logo.txt",
            "r",
            encoding="utf-8",
        ) as logo:
            logo_lines = logo.read().split("\n")
        if not self.oh.debug_mode:
            print("\x1b[2J")
        if terminal_length > (
            len(self.home_list_final)
            + len(self.output_list)
            + len(logo_lines)
            + (terminal_length / 2)
        ):
            for i in range(math.ceil(terminal_length / 2) - len(logo_lines) - 1):
                print()
            spacer = self.long_spacer[: math.floor((terminal_width - 48) / 2)]
            for i in logo_lines:
                print(spacer, i)
            for i in range(
                math.floor(terminal_length / 2)
                - len(self.output_list)
                - len(self.home_list_final)
            ):
                print()
        else:
            for i in range(
                terminal_length - len(self.home_list_final) - len(self.output_list) - 1
            ):
                print()
        for i in self.output_list:
            print("    " + i)
        for i in self.home_list_final:
            print("    " + i)

    def userInput(self) -> str:
        """
        Get an input
        """
        return input("      ")

    def userPassword(self) -> str:
        """
        Get a password
        """
        return getpass.getpass("      ")

    def debug(self, message):
        """
        Print debug messages
        """
        if self.oh.debug_mode:
            print("[DEBUG] " + str(message))
            time.sleep(2)

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

import getpass
import math
import os
import time


class MockAdvancedDisplay:
    """
    Draws the TUI
    """

    def __init__(self, oh):
        self.oh = oh
        self.user_input = ""
        self.user_password = ""

    def clear(self): ...

    def listSet(self, append_object): ...

    def listAppend(self, append_object): ...

    def listPrepend(self, append_object): ...

    def homeSet(self, home_object: str | list, home_length: int = 1): ...

    def output(self): ...

    def userInput(self) -> str:
        return self.user_input

    def userPassword(self) -> str:
        return self.user_password

    def debug(self, message): ...

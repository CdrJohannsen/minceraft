#!/usr/bin/env python
"""
The main file for launching the minceraft launcher

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

import sys


def main():
    """The main function that decides what launcher type should be executed"""
    if "-g" in sys.argv or "--gui" in sys.argv:
        from minceraft import minceraft_gtk  # pylint: disable=import-outside-toplevel

        minceraft_gtk.main()
    else:
        from minceraft import minceraft_tui  # pylint: disable=import-outside-toplevel

        minceraft_tui.main()


if __name__ == "__main__":
    main()

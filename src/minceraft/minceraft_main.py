#!/usr/bin/env python

import sys


def main():
    if "-g" in sys.argv or "--gui" in sys.argv:
        from minceraft import minceraft_gtk

        minceraft_gtk.main()
    else:
        from minceraft import minceraft_tui

        minceraft_tui.main()


if __name__ == "__main__":
    main()

# minceraft
A fast minecraft launcher with integrated text editor.

## Features

- [x] open text editor
- [x] install versions
- [x] authenticate
- [x] launch Minecraft
- [x] manage RAM allocation
- [x] autojoin server on boot
- [x] encrypted credentials
- [x] change skins
- [x] Fabric
- [x] Forge
- [x] CLI/TUI

## Install

```bash
git clone https://github.com/muslimitmilch/minceraft && cd minceraft
# if you have msmcauth and minecraft-launcher-lib already installed
make install
# if you dont have them
make all
```

## Uninstall

```bash
make uninstall
```

## CLI-Usage

```
  -h, --help            show this help message and exit
  -u USER, --user USER  selected user
  -ui USER_INDEX, --user_index USER_INDEX
                        index of selected user. Has higher priority than -u
  -lu, --list_user      list users and their indices
  -p PASSWORD, --password PASSWORD
                        password for user
  -v VERSION, --version VERSION
                        version to launch
  -lv, --list_version   list versions and their indices
```

Tip: 
Use `-p $(cat path/to/password)` instead of `-p PASSWORD` to prevent your password from getting into your bash_history

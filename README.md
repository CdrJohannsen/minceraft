<p align="center">
  <img src="https://raw.githubusercontent.com/muslimitmilch/minceraft/main/src/minceraft.png" width="160" height="160">
</p>

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
- [ ] quickPlay
- [ ] GUI

## Install

```bash
git clone https://github.com/muslimitmilch/minceraft && cd minceraft
```

if you have msmcauth and minecraft-launcher-lib already installed

```bash
make install
```

if you don't have them

```bash
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
  --server IP/URL       server to connect after booting
  --port PORT           port for --server
  -d, --debug           enable debug mode
```

Tip: 
Use `-p $(cat path/to/password)` instead of `-p PASSWORD` to prevent your password from getting into your bash_history

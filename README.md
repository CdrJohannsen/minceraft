<p align="center">
  <img src="https://raw.githubusercontent.com/CdrJohannsen/minceraft/main/src/minceraft/minceraft.png" width="160" height="160">
</p>

# minceraft

A fast minecraft launcher.

<!-- toc -->

- [Features](#features)
- [Install](#install)
- [Uninstall](#uninstall)
- [CLI-Usage](#cli-usage)

<!-- tocstop -->

## Features

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
- [x] GUI (Unmaintained)
- [ ] quickPlay
- [ ] 3D Skin view

## Install

> [!Note]
> If you have minceraft \<=v4.1.0 installed, need to run this command once to update:
>
> ```bash
> make update-install-method
> ```

Make sure you have `pip` installed

```bash
pip install minceraft@git+https://github.com/CdrJohannsen/minceraft.git
```

or if you want to be able to use the gui version

```bash
pip install minceraft[gtk]@git+https://github.com/CdrJohannsen/minceraft.git
```

## Uninstall

```bash
pip uninstall minceraft
```

## CLI-Usage

```
  -h, --help            show this help message and exit
  -g, --gui             Start minceraft in gui mode
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

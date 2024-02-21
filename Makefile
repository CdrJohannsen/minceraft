TUI_SCRIPT=$(HOME)/.minceraft/minceraft/minceraft_tui.py
GUI_SCRIPT=$(HOME)/.minceraft/minceraft/minceraft_gtk.py
GUI_FLAG=
PREEXEC=alacritty -e 

all:
	make install-dependencies
	make install

install:
	make desktop
	make executable
	mkdir -p $(HOME)/.minceraft
	mkdir -p $(HOME)/.minceraft/minceraft
	mkdir -p $(HOME)/.minceraft/skins
	mkdir -p $(HOME)/.minceraft/gameDirs
	mkdir -p $(HOME)/.icons/hicolor/256x256/apps
	mkdir -p $(HOME)/.local/share/applications
	mkdir -p $(HOME)/.local/bin
	cp src/minceraft_gtk.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft_gtk.ui $(HOME)/.minceraft/minceraft/
	cp src/azure.json $(HOME)/.minceraft/minceraft/
	cp src/encryption.py $(HOME)/.minceraft/minceraft/
	cp src/logo.txt $(HOME)/.minceraft/minceraft/
	cp src/minceraft.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft_tui.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft.png $(HOME)/.icons/hicolor/256x256/apps/
	cp src/terminalDisplay.py $(HOME)/.minceraft/minceraft/
	cp src/optionHandler.py $(HOME)/.minceraft/minceraft/
	cp -n src/config.json $(HOME)/.minceraft/ || true
	cp src/minceraft.desktop $(HOME)/.local/share/applications/
	cp src/minceraft $(HOME)/.local/bin/
	rm -f src/mc_edit.py
	rm -f src/mc_launch.py
	python3 ./update_config.py

install-gui:
	make install PREEXEC="" GUI_FLAG="--gui"


executable:
	rm -f src/minceraft
	echo "#!/usr/bin/env bash" >> src/minceraft
	echo 'if [ $$1 == "-g" ] || [ $$1 == "--gui" ]; then' >> src/minceraft
	echo $(GUI_SCRIPT) '$$*' >> src/minceraft
	echo "else" >> src/minceraft
	echo $(TUI_SCRIPT) '$$*' >> src/minceraft
	echo "fi" >> src/minceraft
	chmod +x src/minceraft

desktop:
	rm -f src/minceraft.desktop
	echo -e "[Desktop Entry]\nName=Minceraft\nStartupWMClass=Minceraft" >> src/minceraft.desktop
	echo Exec=$(PREEXEC)$(HOME)/.local/bin/minceraft $(GUI_FLAG) >> src/minceraft.desktop
	echo "Icon=minceraft" >> src/minceraft.desktop
	echo -e "Type=Application\nCategories=Games;\nKeywords=Minceraft, Python, Quick, Fast, Minecraft;" >> src/minceraft.desktop

install-dependencies:
	pip install msmcauth minecraft-launcher-lib argparse

check-uninstall:
	@echo -en "This will remove your entire minceraft installation, including your worlds! \nProceed? [y/N] " && read ans && [ $${ans:-N} = y ]

uninstall:
	make check-uninstall
	rm -f $(HOME)/.local/bin/minceraft
	rm -f $(HOME)/.local/share/applications/minceraft.desktop
	rm -f $(HOME)/.icons/hicolor/256x256/apps/minceraft.png
	rm -rf $(HOME)/.minceraft

shallow-uninstall:
	rm -f $(HOME)/.local/bin/minceraft
	rm -f $(HOME)/.local/share/applications/minceraft.desktop
	rm -f $(HOME)/.icons/hicolor/256x256/apps/minceraft.png
	rm -rf $(HOME)/.minceraft/minceraft

.PHONY: all install install-dependencies uninstall shallow-uninstall desktop executable



all:
	make install-dependencies
	make instal

install:
	make desktop
	make executable
	mkdir -p $(HOME)/.minceraft
	mkdir -p $(HOME)/.minceraft/minceraft
	mkdir -p $(HOME)/.minceraft/skins
	mkdir -p $(HOME)/.icons/hicolor/256x256/apps
	cp -n src/azure.json $(HOME)/.minceraft/minceraft/
	cp src/encryption.py $(HOME)/.minceraft/minceraft/
	cp src/logo.txt $(HOME)/.minceraft/minceraft/
	cp src/mc_edit.py $(HOME)/.minceraft/minceraft/
	cp src/mc_launch.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft.png $(HOME)/.icons/hicolor/256x256/apps/
	cp src/terminalDisplay.py $(HOME)/.minceraft/minceraft/
	cp src/optionHandler.py $(HOME)/.minceraft/minceraft/
	cp src/minceraft.desktop $(HOME)/.local/share/applications/
	cp src/minceraft $(HOME)/.local/bin/

executable:
	rm -f src/minceraft
	echo "#!/usr/bin/env bash" >> src/minceraft
	echo $(HOME)'/.minceraft/minceraft/minceraft.py $$*' >> src/minceraft
	chmod +x src/minceraft

desktop:
	rm -f src/minceraft.desktop
	echo -e "[Desktop Entry]\nName=Minceraft\nStartupWMClass=Minceraft" >> src/minceraft.desktop
	echo Exec=$(TERM)" -e "$(HOME)"/.minceraft/minceraft/minceraft.py" >> src/minceraft.desktop
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
	rm -rf $(HOME)/.config/minceraft
	rm -rf $(HOME)/.minceraft

.PHONY: all install install-dependencies uninstall check-uninstall desktop executable

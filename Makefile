

all:
	make install-dependencies
	make instal

install:
	make desktop
	make executable
	mkdir -p $(HOME)/.minceraft
	mkdir -p $(HOME)/.minceraft/minceraft
	mkdir -p $(HOME)/.minceraft/skins
	cp -n minceraft/azure.json $(HOME)/.minceraft/minceraft/
	cp minceraft/encryption.py $(HOME)/.minceraft/minceraft/
	cp minceraft/logo.txt $(HOME)/.minceraft/minceraft/
	cp minceraft/mc_edit.py $(HOME)/.minceraft/minceraft/
	cp minceraft/mc_launch.py $(HOME)/.minceraft/minceraft/
	cp minceraft/minceraft.py $(HOME)/.minceraft/minceraft/
	cp minceraft/minceraft-icon.png $(HOME)/.minceraft/minceraft/
	cp minceraft/terminalDisplay.py $(HOME)/.minceraft/minceraft/
	cp minceraft/minceraft.desktop $(HOME)/.local/share/applications/
	cp minceraft/minceraft $(HOME)/.local/bin/

executable:
	rm -f minceraft/minceraft
	echo "#!/usr/bin/env bash" >> minceraft/minceraft
	echo $(HOME)/.minceraft/minceraft/minceraft.py >> minceraft/minceraft
	chmod +x minceraft/minceraft

desktop:
	rm -f minceraft/minceraft.desktop
	echo -e "[Desktop Entry]\nName=Minceraft\nStartupWMClass=Minceraft" >> minceraft/minceraft.desktop
	echo Exec=$(TERM)" -e "$(HOME)"/.minceraft/minceraft/minceraft.py" >> minceraft/minceraft.desktop
	echo "Icon="$(HOME)"/.minceraft/minceraft/minceraft-icon.png" >> minceraft/minceraft.desktop
	echo -e "Type=Application\nCategories=Games;\nKeywords=Minceraft, Python, Quick, Fast, Minecraft;" >> minceraft/minceraft.desktop

install-dependencies:
	pip install msmcauth minecraft-launcher-lib argparse

check-uninstall:
	@echo -en "This will remove your entire minceraft installation, including your worlds! \nProceed? [y/N] " && read ans && [ $${ans:-N} = y ]

uninstall:
	make check-uninstall
	rm -f $(HOME)/.local/bin/minceraft
	rm -f $(HOME)/.local/share/applications/minceraft.desktop
	rm -rf $(HOME)/.config/minceraft
	rm -rf $(HOME)/.minceraft

.PHONY: all install install-dependencies uninstall check-uninstall desktop executable

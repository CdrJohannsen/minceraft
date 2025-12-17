
all:
	make install

install:
	# Minceraft is no longer installed with this Makefile
	# 
	# Run this command instead to install minceraft:
	# pip install git+https://github.com/CdrJohannsen/minceraft.git
	# 
	# If you already had minceraft<=v4.1.0 installed, run
	# 	$$ make update-install-method
	# This will update your old installation to the new version
	# After running this command once you should install updates
	# as described above using pip
	
update-install-method:
	@make shallow-uninstall
	mkdir -p $(HOME)/.config/minceraft
	mv $(HOME)/.minceraft/config.json $(HOME)/.config/minceraft/config.json
	mkdir -p $(HOME)/.local/share/minceraft
	mv $(HOME)/.minceraft/* $(HOME)/.local/share/minceraft/
	rm -d $(HOME)/.minceraft/
	pip install minceraft@git+https://github.com/CdrJohannsen/minceraft.git

install-gui:
	make install

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

docs:
	doxygen

tests:
	pytest --cov=src --cov-report=html

analyse:
	pylint src/

.PHONY: uninstall shallow-uninstall tests docs analyse

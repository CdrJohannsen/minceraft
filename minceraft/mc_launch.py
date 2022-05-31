import time, os, msmcauth
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import readchar

def mc_launch(dspl):
	global display
	display = dspl
	homePath = os.path.expanduser('~')
	global minecraft_dir
	minecraft_dir = homePath+'/.minceraft'
	while True:
		display.homeSet('Select Option',2)
		display.listSet('[i]  install version')
		display.listAppend('[r]  reauthenticate')
		selected = readchar.readchar()
		if selected == 'i':
			install()
		elif selected == 'r':
			auth()


#########################################################
#Install
#########################################################

def install():
	display.clear()
	display.homeSet('Select Version',1)
	version = display.userInput()
	display.homeSet('',0)
	display.homeSet('Select Modloader',1)
	display.listSet('[0]  vanilla')
	display.listAppend('[1]  fabric')
	display.listAppend('[2]  forge')
	mod = display.userInput()
	
	current_max = 390
	callback = {
	  "setStatus": set_status,
	  "setProgress": set_progress,
	  "setMax": set_max
	}
	try:
		if mod == '0':
			minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)
		elif mod == '1':
			try:
				minecraft_launcher_lib.fabric.install_fabric(version, minecraft_dir)
			except UnsupportedVersion:
				display.homeSet('Version not supportet by fabric!')
		elif mod == '2':
			forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
			if forge_version is None:
				display.homeSet("This Minecraft Version is not supported by Forge")
			else:
				minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_dir)
		else:
			display.homeSet('Selection not valid!')
	except:
		display.homeSet('Version not avaliable!')
	display.homeSet('Download finished!')
	time.sleep(2)
		
	
	
	
def set_status(status: str):
	  global downloading
	  downloading = status

def set_progress(progress: int):
	prog = f"{progress}/{current_max}"
	size = int(os.get_terminal_size()[0])
	barsize = size-len(prog)-len(str(current_max))-2-4
	barlen = int(round(barsize/current_max,0)*progress)
	bar='['
	for i in range(barlen):
		bar = bar+'='
	for i in range(barsize-barlen):
		bar = bar+'-'
	bar = bar+']'
	display.homeSet(downloading+'\n'+bar+prog)
	a
	


def set_max(new_max: int):
	  global current_max
	  current_max = new_max

#########################################################
#Authenticate
#########################################################

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
	display.homeSet('Select Option',2)
	display.listSet('[i]  install version')
	display.listAppend('[r]  reauthenticate')
	selected = readchar.readchar()
	if selected == 'i':
		install()
	elif selected == 'r':
		auth()


#########################################################

def install():
	display.clear()
	display.homeSet('Select Version',2)
	version = display.userInput()
	display.homeSet('',0)
	os.system('clear')
	current_max = 390
	
	callback = {
	  "setStatus": set_status,
	  "setProgress": set_progress,
	  "setMax": set_max
	}

	minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)
	display.homeSet('Download finished!')
	
def set_status(status: str):
	  global downloading
	  downloading = status

def set_progress(progress: int):
	prog = f"{progress}/{current_max}"
	size = int(os.get_terminal_size()[0])
	barsize = size-len(prog)-current_max-2-4
	barlen = int(round(barsize/current_max,0)*progress)
	bar=''
	for i in range(barlen):
		bar += '='
	for i in range(barsize-barlen):
		bar += '-'
	display.homeSet(downloading+'\n['+bar+']'+prog)
	


def set_max(new_max: int):
	  global current_max
	  current_max = new_max





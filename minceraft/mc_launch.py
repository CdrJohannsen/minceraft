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
	display.set('[i]  install version')
	display.appendTop('[r]  reauthenticate')
	selected = readchar.readchar()
	if selected == 'i':
		install()
	elif selected == 'r':
		auth()


#########################################################

def install():
	display.append('Select Version')
	version = display.userInput()
	
	
	current_max = 390
	def set_status(status: str):
		  display.append(status)
	
	def set_progress(progress: int):
		prog = f"{progress}/{current_max}"
		size = int(os.get_terminal_size()[0])
		barsize = size - len(prog) -2-4
		barlen = int((barsize/current_max)*progress)
		bar=''
		for i in range(barlen):
			bar += '='
		for i in range(barsize-barlen):
			bar += ' '
		display.set('['+bar+']'+prog)
		


	def set_max(new_max: int):
		  global current_max
		  current_max = new_max


	callback = {
		  "setStatus": set_status,
		  "setProgress": set_progress,
		  "setMax": set_max
	}

	minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)


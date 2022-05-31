import time, os, msmcauth
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec

def mc_launch():
	minecraft_dir = homePath+'/.minceraft'
	display.appendTop('[i]  install version')
	display.appendTop('[r]  reauthenticate')
	selected = display.userInput()
	if selected == 'i':
		install()
	elif selected == 'r':
		auth()


#########################################################

def install():
	display.append('Select Version')
	version = display.userInput()
	
	
	current_max = 0
	def set_status(status: str):
		  display.append(status)
	
	def set_progress(progress: int):
		  if current_max != 0:
		      display.append(f"{progress}/{current_max}")


	def set_max(new_max: int):
		  global current_max
		  current_max = new_max


	callback = {
		  "setStatus": set_status,
		  "setProgress": set_progress,
		  "setMax": set_max
	}

	minecraft_launcher_lib.install.install_minecraft_version("1.17", minecraft_dir, callback=callback)


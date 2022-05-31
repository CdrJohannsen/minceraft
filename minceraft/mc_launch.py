import time, os, msmcauth, pickle
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import readchar

def mc_launch(dspl,userDic,userPassword,usr):
	global display
	global userSelected
	userSelected = usr
	display = dspl
	global homePath
	homePath = os.path.expanduser('~')
	global minecraft_dir
	minecraft_dir = homePath+'/.minceraft'
	while True:
		display.homeSet('Select Option',2)
		display.listSet('[i]  install version')
		display.listAppend('[r]  reauthenticate')
		versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
		i=0
		for version in versions:
			display.listAppend('['+str(i)+']  '+version['id'])
			i += 1
		
		selected = readchar.readchar()
		if selected == 'i':
			install()
		elif selected == 'r':
			auth(userPassword,userSelected)
		else:
			try:
				selected = int(selectet)
				launchCommand = minecraft_launcher_lib.command.get_minecraft_command(versions[selected]['id'], minecraft_dir, launchOptions)
				finalLaunchCommand = ''
				for i in launchCommand:
				    finalLaunchCommand += ' ' + i
				os.system('cd '+minecraft_dir+'&& screen -dm '+finalLaunchCommand)
			except:
				display.homeSet('Version not avaliable!')


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

def auth(userPassword,userSelected):
	#try:
		display.homeSet('Authentificating...')
		with open(homePath+'/.config/minceraft/users.bin','rb') as f:
			userDic = pickle.load(f)
			
		email = ec.decrypt(userDic[userSelected]['msEmail'], userPassword)
		msPassword = ec.decrypt(userDic[userSelected]["msPassword"], userPassword)
		resp = msmcauth.login(email, msPassword)
		launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
		userDic[userSelected]['launchOptions'] = launchOptions
		userDic[userSelected]['last_played']['time']=time.time()
		
		with open(homePath+'/.config/minceraft/users.bin','wb') as f:
			pickle.dump(userDic,homePath+'/.config/minceraft/users.bin')
	#except:
		display.homeSet('Authentification failed!')
		time.sleep(2)

#########################################################
#Start
#########################################################

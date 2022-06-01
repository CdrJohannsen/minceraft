import time, os, msmcauth, pickle
import minecraft_launcher_lib
import terminalDisplay
import encryption as ec
import readchar

def mc_launch(dspl,passwd,usr):
	global homePath
	homePath = os.path.expanduser('~')
	global userPassword
	userPassword = passwd
	global userDic
	with open(homePath+'/.config/minceraft/users.bin','rb') as f:
		userDic = pickle.load(f)
	global display
	global userSelected
	userSelected = usr
	display = dspl
	global minecraft_dir
	while True:
		minecraft_dir = homePath+'/.minceraft'
		display.homeSet('Select Option',1)
		display.listSet('[i]  install version')
		display.listAppend('[r]  reauthenticate')
		try:
			versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
			i=0
			for version in versions:
				display.listAppend('['+str(i)+']  '+version['id'])
				i += 1
		except:
			pass
		
		selected = readchar.readchar()
		if selected == 'i':
			install()
		elif selected == 'r':
			auth(userSelected)
		elif selected == '\r':
			version = userDic[userSelected]['last_played']['version']
			if version != '':
				launch(userDic[userSelected]['last_played']['version'])
				break
			else:
				display.homeSet('No version played last!',1)
				time.sleep(2)
		else:
			try:
				selected = int(selected)
				try:
					launch(versions[selected]['id'])
					break
				except Exception as ex:
					display.homeSet('Couldn\'t launch '+versions[selected]['id'])
					print(ex)
					time.sleep(2)
			except Exception as e:
				display.homeSet('Option not avaliable!',1)
				print(e)
				time.sleep(2)
	quit()


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
		success = False
		if mod == '0':
			minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_dir, callback=callback)
			success = True
		elif mod == '1':
			try:
				minecraft_launcher_lib.fabric.install_fabric(version, minecraft_dir, callback=callback)
				success=True
			except UnsupportedVersion:
				display.homeSet('Version not supportet by fabric!',1)
		elif mod == '2':
			forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
			if forge_version is None:
				display.homeSet("This Minecraft Version is not supported by Forge",1)
			else:
				minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_dir, callback=callback)
				success=True
		else:
			display.homeSet('Selection not valid!',1)
			time.sleep(2)
		if success:
			dirs = []
			versionPath=os.path.join(minecraft_dir,'versions')
			for d in os.listdir(versionPath):
				if os.path.isdir(versionPath+'/'+d):
					dirs.append(versionPath+'/'+d)
			new_version = sorted(dirs, key=lambda x: os.path.getctime(x), reverse=True)[:1][0]
			try:
				os.mkdir(os.path.join(minecraft_dir,version))
				os.mkdir(os.path.join(minecraft_dir,os.path.basename(new_version)))
			except:
				pass
			display.homeSet('Download finished!',1)
	except:
		display.homeSet('Version not avaliable!',1)
	time.sleep(2)
		
	
	
	
def set_status(status: str):
	  global downloading
	  downloading = status

def set_progress(progress: int):
	prog = f"{progress}/{current_max}"
	size = int(os.get_terminal_size()[0])
	barsize = size-len(prog)-len(str(current_max))-2-4
	barlen = int(round(barsize/current_max,0)*progress)
	bar='['+'\x1b[37m'
	for i in range(barlen):
		bar = bar+'='
	bar = bar + '\x1b[0m'
	for i in range(barsize-barlen):
		bar = bar+' '
	bar = bar+']'
	display.homeSet(downloading+'\n'+bar+prog,1)
	


def set_max(new_max: int):
	  global current_max
	  current_max = new_max

#########################################################
#Authenticate
#########################################################

def auth(userSelected):
	try:
		display.homeSet('Authentificating...',1)
		email = ec.decrypt(userDic[userSelected]['msEmail'], userPassword)
		msPassword = ec.decrypt(userDic[userSelected]["msPassword"], userPassword)
		resp = msmcauth.login(email, msPassword)
		launchOptions = {"username": resp.username, "uuid": resp.uuid, "token": ec.encrypt(resp.access_token, userPassword)}
		userDic[userSelected]['launchOptions'] = launchOptions
		userDic[userSelected]['last_played']['time']=time.time()
		
		with open(homePath+'/.config/minceraft/users.bin','wb') as f:
			pickle.dump(userDic,f)
	except:
		display.homeSet('Authentification failed!',1)
		time.sleep(2)

#########################################################
#Launch
#########################################################

def launch(version):
	launchOptions = userDic[userSelected]['launchOptions']
	game_dir = minecraft_dir + '/' + version
	launchOptions["gameDirectory"] = game_dir
	try:
		access_token = str(launchOptions['token'])
		display.listAppend(type(access_token))
	except Exception as e:
		display.listAppend(e)
	time.sleep(5)
	try:
		launchOptions['token']=ec.decrypt(access_token,userPassword)
	except:
		display.listAppend(type(access_token))
		display.listAppend('Couldn\'t decrypt access_token')
		display.listAppend(access_token)
	launchOptions['launcherName']='minceraft-launcher'
	launchOptions['launcherVersion']='1.0'
	launchCommand = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_dir, launchOptions)
	finalLaunchCommand = ''
	for i in launchCommand:
	    finalLaunchCommand += ' ' + i
	finalLaunchCommand = 'cd '+game_dir+' && screen -dm '+finalLaunchCommand.replace('--clientId ${clientid} --xuid ${auth_xuid} ','')
	os.system(finalLaunchCommand)
	userDic[userSelected]['last_played']['time']=time.time()
	userDic[userSelected]['last_played']['version']=version
	with open(homePath+'/.config/minceraft/users.bin','wb') as f:
		pickle.dump(userDic,f)
	display.homeSet('Starting '+version,1)
	print(finalLaunchCommand)
	time.sleep(3)

#!/usr/bin/env python3
from os.path import join
import minceraft, terminalDisplay
import os, time

default_delay = 1

class MinecraftTui:
    """
    TUI Interface for Minceraft
    """

    def __init__(self):
        self.oh = minceraft.optionHandler.OptionHandler()
        minceraft.handleArgs(self.oh)
        self.display = terminalDisplay.advancedDisplay(self.oh)
        self.oh.set_debug_callback(self.display.debug)
        if not self.oh.load():
            self.newUser()

    def run(self):
        """
        Starts the TUI Interface
        """

        self.handleAccountSelection()
        self.oh.updateUsers()
        self.oh.updateUserInfo()
        self.oh.updateUsername()
        self.oh.updateVersions()
        self.oh.saveConfig()
        while True:
            if self.selectOption():
                self.oh.saveConfig()
                exit()

    def selectAccount(self):
        """
        Asks the user for their wanted account
        Select 0 for a new account
        """

        users = self.oh.listUsernames()
        userSelection = ['[0]\t\tcreate new user']
        for i in range(len(users)):
            userSelection.append(f"[{i+1}]\t\t{users[i]}")
        self.display.listSet(userSelection)
        user = self.display.userInput()
        try:
            self.oh.user = int(user)
        except:
            self.display.homeSet(['Please choose your user profile',f'Must be a number from 0 to {len(users)}'])
            self.selectAccount()
        self.handleAccountSelection()

    def handleAccountSelection(self):
        """
        Handles if a new account should be created or a login should follow
        """

        if self.oh.user == 0:
            self.newUser()
        else:
            self.oh.updateUsername()
            self.oh.updateUserInfo()
            self.display.clear()
            self.login()

    def login(self):
        """
        Asks for the users password if it doesn't already exsist
        If it is empty the user will return to the account selection
        Checks if the password is correct
        """

        if not self.oh.password:
            self.display.homeSet('Please enter your password for user ' + self.oh.username,1)
            self.oh.password = self.display.userInput()
        if self.oh.password == "":
            self.display.homeSet('Please choose your user profile')
            self.selectAccount()
        if self.oh.user_info["passwordHash"] == minceraft.encryption.hashValue(self.oh.password):
            self.oh.config[0]["last_user"]=self.oh.user
            return
        else:
            self.display.homeSet('Password not correct, try again')
            self.oh.password = self.display.userInput()
            self.login()


    def newUser(self):
        """
        Adds a new User
        """

        self.display.homeSet("Please choose a username")
        username = self.display.userInput()
        password, password2 = 1,2   # Set password to random different values
        while password != password2:
            self.display.homeSet("Please choose a password")
            password = self.display.userInput()
            self.display.homeSet("Please repeat the password")
            password2 = self.display.userInput()
        self.display.homeSet("Select your microsoft authentication")
        while True:
            self.display.listSet('[0]  normal (email & password)')
            self.display.listAppend('[1]  two factor (only for weirdos)')
            auth_type = self.display.userInput()
            if auth_type == "0" or auth_type == "1":
                break
            self.display.homeSet(["Option not avaliable", "Select your microsoft authentication type"])
        auth_successfull = False
        while not auth_successfull:
            if auth_type == "0":
                self.display.listSet('Normal authentication')
                self.display.homeSet("please enter your microsoft email adress")
                email = self.display.userInput()
                self.display.homeSet("please enter your microsoft email password")
                ms_password = self.display.userInput()
                self.display.homeSet("Verifying...",1)
                auth_successfull = minceraft.newNormalAuth(self.oh,username,password,email,ms_password)
                if not auth_successfull:
                    self.display.listSet(['Not a correct microsoft account', 'Please try again'])
                    time.sleep(default_delay)
            else:
                self.display.listSet('Two factor authentication')
                minceraft.twoFactorOpenBrowser()
                self.display.homeSet(["Your browser should have opened","Please paste the url you will be redirected to below"])
                url = self.display.userInput()
                auth_successfull = minceraft.newTwoFactorAuth(self.oh,username,password,url)
                if not auth_successfull:
                    self.display.listSet('The url is not valid, try again')
                    time.sleep(default_delay)
        self.oh.password = password
                
    def selectOption(self):
        """
        Main menu for the TUI launcher
        Select from many options
        """

        if self.oh.version == None:
            selected = self.display.userInput()
            self.display.homeSet('Select Option',1)
            self.display.listSet([self.oh.username,'-------------------------------------'])
            self.display.listAppend('[i]  install version')
            self.display.listAppend('[r]  reauthenticate')
            self.display.listAppend('[d]  delete version')
            self.display.listAppend('[p]  manage preferences')
            self.display.listAppend('[s]  change skin')
            self.display.listAppend('[q]  quit')
            i=0
            for v in self.oh.versions:
                version = v["alias"]
                self.display.listAppend('['+str(i)+']  '+version)
                i+=1
        else:
            selected = None
        if selected == 'i':
            self.install()
            return False

        elif selected == 'r':
            self.display.homeSet('Authenticating...',1)
            if not minceraft.auth(self.oh):
                self.display.homeSet("Authentication failed")
            return False

        elif selected == 'p':
            self.managePrefs()
            return False
            
        elif selected == 's':
            self.manageSkins()
            return False

        if selected == 'q':
            return True
            
        elif selected == 'd':
            self.deleteVersion()
            return False

        elif selected == '':
            version_index = self.oh.user_info['last_played']
            if version_index == -1:
                self.display.homeSet('No version played last!',1)
                time.sleep(default_delay)
                return False
            else:
                self.launch(version_index)
                return True
        else:
            if self.oh.version == None:
                try:
                    self.oh.version = int(selected)
                except:
                    self.display.homeSet('Option not avaliable!',1)
                    time.sleep(default_delay)
                    return False
            if len(self.oh.versions) <= self.oh.version:
                self.display.homeSet(f'Version with index {self.oh.version} not avaliable',1)
                self.oh.version = None
                time.sleep(default_delay)
                return False
            self.launch(self.oh.version)
            return True

    def manageSkins(self):
        """
        Menu for changing skin
        """

        while True:
            self.display.listSet('[q] quit')
            skins = minceraft.listSkins(self.oh)
            for i in range(len(skins)):
                self.display.listAppend(f"[{i}] {skins[i].replace('.png','')}")
            
            self.display.homeSet('Select option')
            index = self.display.userInput()
            if index == 'q':
                return
            else:
                try:
                    index=int(index)
                except:
                    self.display.homeSet('Not a valid option')
                    time.sleep(default_delay)
                    continue
                self.display.homeSet('Choose skin width')
                self.display.listSet('[s] slim')
                self.display.listAppend('[c] classic')
                width = self.display.userInput()
                if width == 's':
                    skinWidth = 'slim'
                elif width == 'c':
                    skinWidth = 'classic'
                else:
                    self.display.homeSet('Not a valid skin type!')
                    time.sleep(default_delay)
                    continue
                minceraft.changeSkin(
                    self.oh,
                    os.path.join(self.oh.minceraftDir,'skins',skins[index]),skinWidth)


    def managePrefs(self):
        while True:
            self.display.listSet([self.oh.username,'-------------------------------------'])
            self.display.homeSet('Select option to modify',1)
            self.display.listAppend('[q] quit')
            for i in range(len(self.oh.versions)):
                self.display.listAppend(f"[{i}] {self.oh.versions[i]['alias']}")
            userInput = self.display.userInput()
            if userInput == 'q':
                return
            try:
                userInput = int(userInput)
            except:
                self.display.homeSet('Not a valid Option')
                time.sleep(default_delay)
                continue
                
            version_prefs = self.oh.versions[userInput]
            while True:
                self.display.homeSet('Select option to modify',1)
                self.display.listSet([self.oh.username,'-------------------------------------'])
                if version_prefs['server'] != '':
                    server_prefs = version_prefs['server']
                    if version_prefs['port'] != '':
                        server_prefs += ' on port: '+version_prefs['port']
                else:
                    server_prefs = 'None'
                
                self.display.listAppend('[q] save & quit')
                self.display.listAppend(f"[0] manage RAM allocation\t\t\t\tCurrent: -Xmx{version_prefs['memory'][0]}G -Xms{version_prefs['memory'][1]}G")
                self.display.listAppend(f"[1] manage servers to connect after launching\tCurrent: {server_prefs}")
                action = self.display.userInput()
                if action == 'q':
                    self.oh.saveConfig()
                    break
                elif action == '0':
                    self.display.homeSet('Specify max RAM allocation in GB')
                    max_ram = self.display.userInput()
                    try:
                        max_ram = int(max_ram)
                        self.display.homeSet('Specify min RAM allocation in GB')
                        min_ram = self.display.userInput()
                        try:
                            min_ram = int(min_ram)
                            version_prefs["memory"][0]=max_ram
                            version_prefs["memory"][1]=min_ram
                        except:
                            self.display.homeSet('Not a number')
                            time.sleep(default_delay)
                    except:
                        self.display.homeSet('Not a number')
                        time.sleep(default_delay)
                elif action == '1':
                    self.display.homeSet('Set server ip')
                    ip = self.display.userInput()
                    self.display.homeSet('If needed set server port')
                    port = self.display.userInput()
                    version_prefs['server'] = ip
                    version_prefs['port'] = port


    def deleteVersion(self):
        """
        Selects the version to delete and calls minceraft.deleteVersion() for deletion
        """

        self.display.homeSet('Select version to delete',1)
        self.display.listSet('[q]  quit')
        for i in range(len(self.oh.versions)):
            self.display.listAppend('['+str(i)+']  '+self.oh.versions[i]["alias"])
        del_version = self.display.userInput()
        if del_version != 'q':
            try:
                del_version = int(del_version)
            except:
                self.display.homeSet("Must be a number")
                return
            if del_version >= len(self.oh.versions):
                self.display.homeSet(f"Must be between 0 and {len(self.oh.versions)-1}")
            else:
                minceraft.deleteVersion(self.oh,del_version)

    def launch(self,version_index):
        """
        Calls the minceraft.launch command and displays the startet version
        """
        
        self.display.homeSet(f"Preparing to launch {self.oh.versions[version_index]['alias']}")
        minceraft.launch(self.oh,version_index)
        self.display.homeSet(f"Starting {self.oh.versions[version_index]['alias']}")
        time.sleep(3)

    def install(self):
        """
        Handles the selection of the version, modloader and alias for the install
        """
        self.display.clear()
        latest=minceraft.minecraft_launcher_lib.utils.get_latest_version()
        self.display.homeSet(['Select Version','For manual install paste name of directory',f'Latest release: {latest["release"]}  Latest snapshot: {latest["snapshot"]}'])
        version = self.display.userInput()
        self.display.homeSet('')
        self.display.homeSet('Select Modloader')
        self.display.listSet('[0]  vanilla')
        self.display.listAppend('[1]  fabric')
        self.display.listAppend('[2]  forge')
        self.display.listAppend('[3]  manual install')
        modloader = self.display.userInput()
        if not modloader in ["","0","1","2","3"]:
            self.display.homeSet("Not a valid Modloader")
            return
        self.display.clear()
        self.display.homeSet(['Default is version','Select Name'])
        alias = self.display.userInput()
        self.install_max = 390
        callback = {
          "setStatus": self.set_status,
          "setProgress": self.set_progress,
          "setMax": self.set_max
        }
        self.display.clear()
        self.display.homeSet('')
        version_unavaliable = minceraft.is_version_valid(self.oh,version,modloader)
        # True: Vanilla version not avaliable
        # False: Version not supportet by modloader
        # None: Version supportet
        if version_unavaliable:
            self.display.homeSet("Version not avaliable")
        elif version_unavaliable == False:
            if modloader == 1:
                self.display.homeSet("Version not supportet by Fabric")
            elif modloader == 2:
                self.display.homeSet("Version not supportet by Forge")
        else:
            minceraft.install(self.oh,version,modloader,alias,callback)


    def set_status(self,status: str):
          temp_stat = "{:<25}".format(status)
          self.install_status = temp_stat[:25]


    def set_progress(self,progress: int):
        prog = f"{progress}/{self.current_max}"
        size = int(os.get_terminal_size()[0])
        barsize = size-len(prog)-len(str(self.current_max))-2-4-30
        barlen = int(((float(barsize)/(float(self.current_max)/10))*(progress/10)))
        bar='  ['
        for i in range(barlen):
            bar = bar+'■'
        for i in range(barsize-barlen):
            bar = bar+' '
        bar = bar
        out = '('+prog+')'+((11-len(prog))*' ')+self.install_status+bar
        final = out+(size-len(out)-1)*' '+']'
        print(final+'\r', end='')


    def set_max(self,new_max: int):
          self.current_max = new_max





if __name__ == "__main__":
    mc_tui = MinecraftTui()
    mc_tui.run()

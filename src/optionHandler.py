import minceraft, os, json

class OptionHandler:
    def __init__(self):
        self.homePath = os.path.expanduser('~')
        self.minceraftDir = os.path.join(self.homePath,".minceraft")
        self.versionsDir = os.path.join(self.minceraftDir,"versions")
        self.gameDirs = os.path.join(self.minceraftDir,"gameDirs")
        self.configPath = os.path.join(self.homePath, ".minceraft/config.json")
        self.config = []
        self.reloadConfig()
        self.password = None
        self.version = 0
        self.versions = []
        self.user_info = []
        self.users = []
        self.username = None
        self.server = None
        self.port = None
        self.debug_mode = False
        self.debug = print
        self.user=0
        self.user = self.config[0]["last_user"]
        self.updateUsers()

    def load(self):
        if len(self.config) == 1:
            return False
        self.updateUsers()
        self.updateUserInfo()
        self.updateUsername()
        self.updateVersions()
        return True

    def updateVersions(self):
        self.versions = self.user_info["versions"]

    def updateUsers(self):
        self.users = self.config[1:]

    def updateUserInfo(self):
        self.user_info = self.config[self.user]

    def updateUsername(self):
        self.username = self.config[self.user]["username"]

    def reloadConfig(self) -> None:
        with open(self.configPath,"r") as f:
            self.config = json.load(f)

    def saveConfig(self) -> None:
        with open(self.configPath,"w") as f:
            json.dump(self.config, f, indent=4)

    def listUsernames(self) -> list:
        usernames = []
        for i in self.users:
            usernames.append(i["username"])
        return usernames

    def set_debug_callback(self,callback) -> None:
        self.debug = callback

    def from_args(self, args) -> None:
        if args.user_index:
            self.user = args.user_index
            if args.user_index > len(self.users):
                print(f"Index must be between 0 and {len(self.users)}")
                exit()
        else:
            if args.user in self.listUsernames():
                self.user = self.listUsernames().index(args.user)+1
            elif args.user == None:
                pass
            else:
                print(f"User {args.user} does not exsist")
                exit()
        self.password = args.password
        self.version = args.version
        if self.version != None:
            self.updateUserInfo()
            self.updateVersions()
            self.version -= 1
            if self.version > len(self.user_info["versions"])-1:
                print(f"Index out of range. Version must be between 0 and {len(self.user_info['versions'])-1}")
                exit()
        self.server = args.server
        self.port = args.port
        self.debug_mode = args.debug
        if args.list_user:
            self.cliListUsers()
            exit()
        if args.list_version:
            self.cliListVersions()
            exit()

    def cliListUsers(self) -> None:
        users = self.listUsernames()
        print("[INDEX]\t\tUSER")
        for i in range(len(users)):
            users[i] = f"[{str(i+1)}]\t\t{users[i]}"
            print(users[i])

    def cliListVersions(self) -> None:
        if not self.user:
            print("No user specified")
            exit()
        self.updateUserInfo()
        self.updateVersions()
        i = 1
        print(f'[INDEX]\t\tVERSION')
        for v in self.versions:
            print(f'[{str(i)}]\t\t{v["alias"]}')
            i+=1

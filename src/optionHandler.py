import minceraft, os, json

class OptionHandler:
    def __init__(self):
        self.users = minceraft.listUsers()
        self.user
        self.password
        self.version
        self.server
        self.port
        self.debug_mode
        self.debug = print

    def set_debug_callback(self,callback: function):
        self.debug = callback

    def from_args(self, args) -> None:
        if args.user_index:
            self.user = args.user_index
            if args.user_index > len(self.users):
                print(f"Index must be between 0 and {len(self.users)}")
                exit()
        else:
            if args.user in self.users:
                self.user = self.users.index(args.user)+1
            elif args.user == None:
                self.user = None
            else:
                print(f"User {args.user} does not exsist")
                exit()
        self.password = args.password
        self.version = args.version
        self.server = args.server
        self.port = args.port
        self.debug_mode = args.debug
        if args.list_user:
            self.listUsers()
            exit()
        if args.list_version:
            self.listVersions()
            exit()
    
    def listUsers(self):
        users = minceraft.listUsers()
        print("[INDEX]\t\tUSER")
        for i in range(len(users)):
            users[i] = f"[{str(i+1)}]\t\t{users[i]}"
            print(users[i])

    def listVersions(self):
        if not self.user:
            print("No user specified")
            exit()
        with open(os.path.expanduser('~')+'/.config/minceraft/versions.json','r') as f:
            versionList = json.load(f)
        i = 0
        print(f'[INDEX]\t\tVERSION')
        for v in list(versionList[self.user-1]):
            version = str(v[0])
            print(f'[{str(i)}]\t\t{version}')
            i+=1

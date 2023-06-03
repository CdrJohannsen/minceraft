import minceraft

class OptionHandler:
    def __init__(self, args) -> None:
        if args.user_index:
            self.user = args.user_index
        else:
            users = minceraft.listUsers()
            if args.user in users:
                self.user = users.index(args.user)+1
            elif args.user == None:
                self.user = None
            else:
                print(f"User {args.user} does not exsist")
                exit()
        self.password = args.password
        self.version = args.version
        if args.list_user:
            users = minceraft.listUsers()
            print("[INDEX]\t\tUSER")
            for i in range(len(users)):
                users[i] = f"[{str(i+1)}]\t\t{users[i]}"
                print(users[i])
            exit()

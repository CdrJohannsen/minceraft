#!/usr/bin/env python3
import json, os
homePath = os.path.expanduser('~')

# Assume that if preferences.json exists the old config is still used
try:
    with open(os.path.join(homePath,".config","minceraft","preferences.json"), "r") as f:
        prefs=json.load(f)
    very_old_config=True
except:
    print("Not the oldest config")
    very_old_config=False

if very_old_config:
    """
    For the old config that was in .config/minceraft
    """
    with open(os.path.join(homePath,".config","minceraft","users.json"), "r") as f:
        users=json.load(f)
    with open(os.path.join(homePath,".config","minceraft","versions.json"), "r") as f:
        versions=json.load(f)

    config = []

    config.append({})
    config[0]["last_user"] = prefs[0]["last_user"]+1
    config[0]["config_version"] = 2.0
    config[0]["launcher_version"] = "3.0"
    for i in range(len(users)):
        user = users[i]
        pref = prefs[i+1]
        vers = versions[i]
        user["last_time"]=pref["last_time"]
        user["last_played"]=pref["last_played"][1]
        new_versions=[]
        for j in range(len(pref["versions"])):
            version = {}
            v = pref["versions"][j]
            version["version"] = v["version"]
            version["alias"] = vers[j][0]
            version["quickPlay"]=0
            memory = []
            memory.append(v["RAM"][0][4:-1])
            memory.append(v["RAM"][1][4:-1])
            version["memory"] = memory
            version["server"] = v["server"]
            version["port"] = v["port"]
            new_versions.append(version)
        user["versions"] = new_versions
        config.append(user)


    with open(os.path.join(homePath,".minceraft","config.json"), "w") as f:
        json.dump(config,f,indent=4)

    gameDirs = os.path.join(homePath,".minceraft","gameDirs")
    for user in versions:
        for version in user:
            if version[0] != version[1]:
                os.system(f"mv {os.path.join(gameDirs,version[1])} \"{os.path.join(gameDirs,version[0].replace(' ','-'))}\"")
    os.system(f"mv {os.path.join(homePath,'.config','minceraft')} {os.path.join(homePath,'.config','minceraft_old')}")
else:
    print("Updating launcher_version")
    with open(os.path.join("src","config.json"),"r") as f:
        empty_config = json.load(f)
    with open(os.path.join(homePath,".minceraft","config.json"),"r") as f:
        current_config = json.load(f)
        current_config[0]["launcher_version"]=empty_config[0]["launcher_version"]
    with open(os.path.join(homePath,".minceraft","config.json"),"w") as f:
        json.dump(current_config,f,indent=4)

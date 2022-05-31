def encrypt(string, key):
    while(len(key) < len(string)):
        key += key
    encryptedString = ""
    for i in range(len(string)):
        encryptedString += chr(ord(string[i]) + ord(key[i]))
    return(encryptedString)


def decrypt(string, key):
    while(len(key) < len(string)):
        key += key
    decryptedString = ""
    for i in range(len(string)):
        decryptedString += chr(ord(string[i]) - ord(key[i]))
    return(decryptedString)

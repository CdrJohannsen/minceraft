#    Minceraft-launcher is a fast launcher for minecraft
#    Copyright (C) 2022  Cdr_Johannsen, Muslimitmilch
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
import hashlib

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


def hashValue(inputString):
    hash = hashlib.new('sha256')
    encodedString = inputString.encode()
    hash.update(encodedString)
    return(hash.hexdigest())

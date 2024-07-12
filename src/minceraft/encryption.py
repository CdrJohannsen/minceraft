"""
Encryption functions

Minceraft-launcher is a fast launcher for minecraft
Copyright (C) 2024  Cdr_Johannsen, Muslimitmilch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import hashlib


def encrypt(string, key) -> str:
    """
    Encrypt a string
    """
    while len(key) < len(string):
        key += key
    encrypted_string = ""
    for i in range(len(string)):
        encrypted_string += chr(ord(string[i]) + ord(key[i]))
    return encrypted_string


def decrypt(string, key) -> str:
    """
    Decrypt a string
    """
    while len(key) < len(string):
        key += key
    decrypted_string = ""
    for i in range(len(string)):
        decrypted_string += chr(ord(string[i]) - ord(key[i]))
    return decrypted_string


def hashValue(input_string) -> str:
    """
    Hash a string
    """
    hashed = hashlib.new("sha256")
    encoded_string = input_string.encode()
    hashed.update(encoded_string)
    return hashed.hexdigest()

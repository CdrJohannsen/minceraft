import hashlib
import sys

import pytest

sys.path.append("src/")
from minceraft.encryption import decrypt, encrypt, hashValue


def test_encrypt():
    original_string = "Hello World"
    key = "12345678"
    expected_string = "\x79\x97\x9f\xa0\xa4\x56\x8e\xa7\xa3\x9e\x97"

    encrypted_string = encrypt(original_string, key)

    assert encrypted_string == expected_string


def test_decrypt():
    original_string = "\x79\x97\x9f\xa0\xa4\x56\x8e\xa7\xa3\x9e\x97"
    key = "12345678"
    expected_string = "Hello World"

    encrypted_string = decrypt(original_string, key)

    assert encrypted_string == expected_string


def test_hashValue():
    original_string = "Hello World"
    original_string = original_string
    expected_string = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"

    encrypted_string = hashValue(original_string)

    assert encrypted_string == expected_string

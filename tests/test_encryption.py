import hashlib
import sys

import pytest

sys.path.append("src/")
from minceraft.encryption import decryptAES, encryptAES, hashValue


def test_encrypt():
    original_string = "Hello World"
    key = "12345678"
    expected_string = "23f9111f734be76196b6b16883ba23a2"

    encrypted_string = encryptAES(original_string, key)

    assert encrypted_string == expected_string


def test_decrypt():
    original_string = "23f9111f734be76196b6b16883ba23a2"
    key = "12345678"
    expected_string = "Hello World"

    encrypted_string = decryptAES(original_string, key)

    assert encrypted_string == expected_string


def test_hashValue():
    original_string = "Hello World"
    original_string = original_string
    expected_string = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"

    encrypted_string = hashValue(original_string)

    assert encrypted_string == expected_string

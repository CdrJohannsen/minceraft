import json
import os
import shutil
import sys
import tempfile
import time

import pytest
from mock_optionHandler import MockOptionHandler

sys.path.append("src/")
from minceraft import minceraft
from minceraft.optionHandler import OptionHandler


class TestMinceraft:
    @pytest.fixture
    def oh(self):
        option_handler = MockOptionHandler()
        option_handler.reloadConfig()
        option_handler.updateUsers()

        with open(option_handler._config_file.name, "r", encoding="utf-8") as f:
            self.example_config = json.load(f)

        self.example_user_info: dict = {
            "username": "Max Mustermann",
            "passwordHash": "hash",
            "msEmail": "max.mustermann@example.com",
            "msPassword": "examplePassword",
            "authType": "normal",
            "last_time": time.time(),
            "launchOptions": {
                "username": "MMustermann",
                "uuid": "exampleUuid",
                "token": "exampleToken",
            },
            "last_played": -1,
            "versions": [],
        }

        yield option_handler

    def test_addUser(self, oh):
        minceraft.addUser(oh, self.example_user_info)

        expected_config = list(self.example_config)
        expected_config.append(self.example_user_info)

        with open(oh._config_file.name, "r", encoding="utf-8") as f:
            generated_config = json.load(f)

        assert expected_config == generated_config

    def test_deleteVersionNotPlayed(self, oh: OptionHandler):
        oh.load()

        minceraft.deleteVersion(oh, 0)

        assert len(oh.versions) == 1
        assert oh.user_info["last_played"] == -1

    def test_deleteVersionLastPlayed(self, oh: OptionHandler):
        oh.config[1]["last_played"] = 0
        oh.load()

        minceraft.deleteVersion(oh, 0)

        assert len(oh.versions) == 1
        assert oh.user_info["last_played"] == -1

    def test_deleteVersionGreaterLastPlayed(self, oh: OptionHandler):
        oh.config[1]["last_played"] = 1
        oh.load()

        minceraft.deleteVersion(oh, 0)

        assert len(oh.versions) == 1
        assert oh.user_info["last_played"] == 0

    def test_isVersionValidNoVanilla(self, oh: OptionHandler):
        oh.load()
        minceraft.minecraft_launcher_lib.utils.is_version_valid = lambda *_: False

        is_valid = minceraft.isVersionValid(oh, "invalid-version", "0")

        assert is_valid == True

    def test_isVersionValidNoFabric(self, oh: OptionHandler):
        oh.load()
        minceraft.minecraft_launcher_lib.utils.is_version_valid = lambda *_: True
        minceraft.minecraft_launcher_lib.fabric.is_minecraft_version_supported = lambda _: False

        is_valid = minceraft.isVersionValid(
            oh, "18w43a", "1"
        )  # The fabric wiki states that snapshot 18w43b and above are supported

        assert is_valid == False

    def test_isVersionValidNoForge(self, oh: OptionHandler):
        oh.load()
        minceraft.minecraft_launcher_lib.utils.is_version_valid = lambda *_: True
        minceraft.minecraft_launcher_lib.forge.find_forge_version = lambda _: False

        is_valid = minceraft.isVersionValid(oh, "1.0", "2")

        assert is_valid == False

    def test_isVersionValid(self, oh: OptionHandler):
        oh.load()
        minceraft.minecraft_launcher_lib.utils.is_version_valid = lambda *_: True
        minceraft.minecraft_launcher_lib.fabric.is_minecraft_version_supported = lambda _: True

        is_valid = minceraft.isVersionValid(oh, "18w43b", "1")

        assert is_valid == None

    def test_generateVersion(self, oh: OptionHandler):
        oh.load()

        minceraft.generateVersion(oh, "test-version", "Test version", 0)

        assert oh.versions[-1]["version"] == "test-version"
        assert oh.versions[-1]["alias"] == "Test version"
        assert oh.versions[-1]["quickPlay"] == 0

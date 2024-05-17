import json
import os
import sys
from shutil import copy
from tempfile import NamedTemporaryFile

import pytest

sys.path.append("src/")
from optionHandler import OptionHandler


class TestOptionHandler:
    @pytest.fixture
    def option_handler(self):
        self.config = NamedTemporaryFile()
        copy(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_config.json"),
            self.config.name,
        )

        ohandler = OptionHandler()
        ohandler.config_path = self.config.name
        with open(self.config.name, "r", encoding="utf-8") as f:
            self.example_config = json.load(f)

        yield ohandler

    def test_versions_dir(self, option_handler):
        assert option_handler.versions_dir == os.path.join(os.path.expanduser("~"), ".minceraft", "versions")

    def test_game_dirs(self, option_handler):
        assert option_handler.game_dirs == os.path.join(os.path.expanduser("~"), ".minceraft", "gameDirs")

    def test_config_path(self, option_handler):
        option_handler.__init__()

        assert option_handler.config_path == os.path.join(os.path.expanduser("~"), ".minceraft", "config.json")

    def test_updateVersions(self, option_handler):
        option_handler.user_info["versions"] = list(self.example_config[1]["versions"])

        option_handler.updateVersions()

        assert option_handler.user_info["versions"] == list(self.example_config[1]["versions"])

    def test_updateUserinfo(self, option_handler):
        option_handler.user = 1

        option_handler.updateUserInfo()

        assert option_handler.user_info["username"] == "Cdr_Johannsen"

    def test_updateUsername(self, option_handler):
        option_handler.user = 1

        option_handler.updateUsername()

        assert option_handler.username == "Cdr_Johannsen"

    def test_load_noUsers(self, option_handler):
        option_handler.config = self.example_config[:1]

        load_success = option_handler.load()

        assert load_success == False

    def test_load_hasUsers(self, option_handler):
        option_handler.config = self.example_config

        load_success = option_handler.load()

        assert load_success == True
        assert option_handler.user_info["versions"] == list(self.example_config[1]["versions"])
        assert option_handler.user_info["username"] == "Cdr_Johannsen"
        assert option_handler.username == "Cdr_Johannsen"

    def test_listUsernames(self, option_handler):
        option_handler.config = self.example_config
        option_handler.load()

        user_list = option_handler.listUsernames()

        assert user_list == ["Cdr_Johannsen"]

    def test_setDebugCallback(self, option_handler):
        option_handler.setDebugCallback(print)

        assert option_handler.debug == print

    def test_cliListUsers(self, option_handler, capsys):
        option_handler.config = self.example_config
        option_handler.load()

        option_handler.cliListUsers()

        out, err = capsys.readouterr()

        assert out == "[INDEX]\t\tUSER\n[1]\t\tCdr_Johannsen\n"

    def test_cliListVersions(self, option_handler, capsys):
        option_handler.config = self.example_config
        option_handler.load()

        option_handler.cliListVersions()

        out, err = capsys.readouterr()

        assert out == "[INDEX]\t\tVERSION\n[1]\t\t1.20.1 Vanilla\n[2]\t\t1.20.1 Vanilla\n"

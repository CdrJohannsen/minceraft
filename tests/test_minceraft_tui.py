import sys

import pytest
from mock_optionHandler import MockOptionHandler
from mock_terminalDisplay import MockAdvancedDisplay

sys.path.append("src/")
import minceraft_tui
import terminalDisplay

minceraft_tui.minceraft.OptionHandler = MockOptionHandler
terminalDisplay.AdvancedDisplay = MockAdvancedDisplay
minceraft_tui.minceraft.handleArgs = lambda _: ...


class TestMinceraftTUI:
    @pytest.fixture
    def mc_tui(
        self,
    ):
        yield minceraft_tui.MinecraftTui()

    def test_init(self, mc_tui): ...

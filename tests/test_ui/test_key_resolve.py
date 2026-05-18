from textual import events
from dooit.ui.api.api_components.keys import KeyMatchType
from dooit.ui.api.events import Startup
from tests.test_ui.ui_base import run_pilot
from dooit.ui.tui import Dooit
from dooit.ui.screens import MainScreen
from dooit.utils.default_config import key_setup


async def test_base_screen_keys():
    async with run_pilot() as pilot:
        app = pilot.app
        assert isinstance(app, Dooit)

        await pilot.pause()
        screen = app.screen

        assert isinstance(screen, MainScreen)

        assert screen.resolve_key(events.Key("home", None)) == "home"
        assert screen.resolve_key(events.Key("space", " ")) == " "


def test_c_does_not_match_ctrl_e_prefix():
    from dooit.ui.api.dooit_api import DooitAPI

    app = Dooit(":memory:")
    api = DooitAPI(app)
    key_setup(api, Startup())

    match = api.keys.register_key("c")
    assert match.match_type == KeyMatchType.MatchFound
    assert match.function is not None
    assert api.keys.input == ""

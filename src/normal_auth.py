"""
Authentification code for non-2fa

Minceraft-launcher is a fast launcher for minecraft
Copyright (C) 2025  Cdr_Johannsen, Muslimitmilch

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

from re import Match, search
from typing import NamedTuple
from urllib.parse import quote, unquote

import requests as r

PREP = "https://login.live.com/oauth20_authorize.srf?client_id=000000004C12AE6F&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"  # pylint: disable=line-too-long
XBOX_LIVE = "https://user.auth.xboxlive.com/user/authenticate"
XSTS = "https://xsts.auth.xboxlive.com/xsts/authorize"
MC_XBOX = "https://api.minecraftservices.com/authentication/login_with_xbox"
PROFILE = "https://api.minecraftservices.com/minecraft/profile"

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0"

APP_JSON = "application/json"


class LoginInfo(NamedTuple):
    """The info needed to launch the game"""

    access_token: str
    username: str
    uuid: str


class LoginException(Exception):
    """Custom Exception for this module"""


def prepare(session: r.Session) -> tuple[str, str]:
    """Get the url and sFFTag for the next step"""
    resp = session.get(PREP, allow_redirects=True)

    sfft_res: Match[str] | None = search(r"sFTTag\":\"<(.*?)>\"", resp.text)
    if sfft_res is None:
        raise LoginException("Couldn't find sFFTag")

    sfft = sfft_res.group(1)
    sfft_value_res = search('value=\\\\"(.+?)\\\\', sfft)
    if sfft_value_res is None:
        raise LoginException("Couldn't find sFFTag value")
    sfft_value = sfft_value_res.group(1)

    url_post_res = search(r"urlPost\":\"(.+)\"", resp.text)
    if url_post_res is None:
        raise LoginException("Couldn't find urlPost")
    url_post = url_post_res.group(1)

    return (sfft_value, url_post)


def getAccessToken(session: r.Session, email: str, password: str, sfft: str, url: str) -> str:
    """Sign in to Microsoft"""
    data = f"login={quote(email)}&loginfmt={quote(email)}&passwd={quote(password)}&PPFT={quote(sfft)}"

    resp = session.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

    if "accessToken" not in resp.url:
        if "Sign in to" in resp.text:
            raise LoginException("Wrong credentials")
        if "Help us protect your account" in resp.text:
            raise LoginException("Account has 2fa enabled")

    fragment = resp.url.split("#")[1]
    fragment_dict = dict(item.split("=") for item in fragment.split("&"))
    return unquote(fragment_dict["access_token"])


def xblSignin(session: r.Session, access_token: str) -> tuple[str, str]:
    """Sign in to XBox Live"""
    payload = {
        "Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": access_token},
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }

    resp = session.post(XBOX_LIVE, json=payload, headers={"Content-Type": APP_JSON, "Accept": APP_JSON})

    data = resp.json()

    return (data["Token"], data["DisplayClaims"]["xui"][0]["uhs"])


def getXstsToken(session: r.Session, token: str) -> str:
    """Get the XSTS Token"""
    payload = {
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
        "Properties": {"SandboxId": "RETAIL", "UserTokens": [token]},
    }

    resp = session.post(XSTS, json=payload, headers={"Accept": APP_JSON})

    data = resp.json()

    if resp.status_code != 200:
        if data["XErr"] == 2148916238:
            raise LoginException("This child account needs to be added to a family")
        if data["XErr"] == 2148916233:
            raise LoginException("This account has no XBox account")

    return data["Token"]


def getBearerToken(session: r.Session, xsts_token: str, user_hash: str) -> str:
    """Get the actual token needed to launch the game"""
    payload = {"identityToken": f"XBL3.0 x={user_hash};{xsts_token}", "ensureLegacyEnabled": True}

    resp = session.post(MC_XBOX, json=payload, headers={"Content-Type": APP_JSON, "Accept": APP_JSON})

    data = resp.json()
    return data["access_token"]


def getProfileInfo(session: r.Session, bearer: str) -> tuple[str, str]:
    """Get profile information"""
    resp = session.get(PROFILE, headers={"Authorization": f"Bearer {bearer}"})

    if resp.status_code != 200:
        raise LoginException(f"Failed to get profile info: {resp.status_code}")

    data = resp.json()

    return data["name"], data["id"]


def login(email: str, password: str) -> LoginInfo:
    """Login to a Minecraft account using the non-2fa method"""
    session = r.Session()
    session.headers["User-Agent"] = USER_AGENT

    sfft, url = prepare(session)

    access_token = getAccessToken(session, email, password, sfft, url)

    token, user_hash = xblSignin(session, access_token)

    xsts_token = getXstsToken(session, token)

    bearer = getBearerToken(session, xsts_token, user_hash)

    name, uuid = getProfileInfo(session, bearer)

    return LoginInfo(bearer, name, uuid)

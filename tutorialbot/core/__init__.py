from collections import abc
from typing import TYPE_CHECKING, cast

import disnake
from dotenv import load_dotenv
from dynaconf import Dynaconf

if TYPE_CHECKING:
    from dataclasses import dataclass

    @dataclass
    class _BotGroup:
        token: str
        secret: str
        redirect_uri: str
        client_id: str
        env: str

    @dataclass
    class _LogGroup:
        level: str
        open_telemetry_endpoint: str

    class _EmojiGroup(abc.Mapping[str, str]):
        def __getattr__(self, name: str) -> str: ...

    class _ColorGroup(abc.Mapping[str, int]):
        def __getattr__(self, name: str) -> int: ...

    @dataclass
    class Settings:
        bot: _BotGroup
        log: _LogGroup

        emojis: _EmojiGroup
        colors: _ColorGroup


load_dotenv(override=True)

settings = cast(
    "Settings",
    Dynaconf(
        envvar_prefix="TUTORIALBOT",
        load_dotenv=True,
        merge_enabled=True,
        settings_files=[
            "assets/settings/colors.toml",
            "assets/settings/emojis.toml",
        ],
    ),
)

emojis = settings.emojis
colors = settings.colors

if not settings.bot.token:
    raise RuntimeError("The bot token is missing")

disnake.Embed.set_default_colour(settings.colors.embed)

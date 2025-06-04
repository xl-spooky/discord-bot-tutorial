import asyncio
import signal
import sys

import disnake
from disnake.ext.commands import CommandSyncFlags
from loguru import logger
from tutorialbot.bot import TutorialBot, __author__, __version__
from tutorialbot.core import logging, settings
from tutorialbot.ext.http import HttpClient


async def main() -> None:
    """Entry point for starting the TutorialBot bot.

    This function configures logging, prints version and author information, determines the bot's
    presence (status and activity) based on the environment, initializes intents, creates the bot
    instance, loads all extensions, and sets up graceful shutdown handling. 
    It then logs into Discord, establishes HTTP client sessions, and finally connects the bot 
    to start receiving events.

    Steps performed:
    1. Initialize logging configuration.
    2. Log the current version and author of the bot.
    3. Choose activity and status depending on whether the environment is 'DEV' or not.
    4. Define Discord intents required for the bot to function 
        (including members and message content).
    5. Instantiate the TutorialBot bot with the specified 
        prefix, allowed mentions, activity, status, and intents.
    6. Load all extensions from the 
        `./tutorialbot/bot/extensions` directory.
    7. Create an asyncio.Event (`shutdown_event`) to signal when a shutdown sequence should begin.
    8. Define and register a signal handler (`_signal_handler`) for SIGINT, SIGTERM 
        (and SIGBREAK on Windows)
        that will log a shutdown message, schedule the bot to close, and set the shutdown event.
    9. Start the bot login task inside an asyncio.TaskGroup to authenticate with Discord.
    10. Create HTTP client sessions (regular and authenticated) and then create a TaskGroup to run 
        the bot connection concurrently. This ensures that HTTP routes and the bot connection 
        are active simultaneously.
    """
    logging.setup()
    logger.info(f"Running tutorialbot v{__version__} ({settings.bot.env})")
    logger.info(f"By {__author__}")

    if settings.bot.env == "DEV":
        activity = disnake.Game(name="[DEV] Bot in development...")
        status = disnake.Status.dnd
    else:
        activity = disnake.Game(name=f"Running version {__version__}")
        status = disnake.Status.online

    intents = disnake.Intents.default() | disnake.Intents.members | disnake.Intents.message_content

    bot = TutorialBot(
        command_prefix=[","],
        allowed_mentions=disnake.AllowedMentions.all(),
        activity=activity,
        status=status,
        intents=intents,
        command_sync_flags=CommandSyncFlags.default(),
    )

    bot.load_extensions("./tutorialbot/bot/extensions")

    shutdown_event = asyncio.Event()

    def _signal_handler(*_: object) -> None:
        """Signal handler for graceful shutdown of the bot.

        When a termination signal is received, this function logs a shutdown message,
        schedules the bot to close its connection to Discord, and sets the shutdown event
        so that any waiting coroutines can proceed with cleanup.
        """
        logger.info("Shutting down…")
        bot.loop.create_task(bot.close())
        shutdown_event.set()

    signals = [signal.SIGINT, signal.SIGTERM]
    if sys.platform == "win32":
        signals.append(signal.SIGBREAK)

    for signal_ in signals:
        try:
            bot.loop.add_signal_handler(signal_, _signal_handler)
        except NotImplementedError:
            # On platforms where add_signal_handler isn't available (e.g., Windows),
            # fallback to the standard signal.signal registration.
            signal.signal(signal_, _signal_handler)

    # first, log in without actually connecting so that token validation happens early.
    async with asyncio.TaskGroup() as tg:
        tg.create_task(bot.login(settings.bot.token))

    # create HTTP sessions (one general, one authenticated) and then connect the bot concurrently.
    async with (
        HttpClient.create_session(),
        HttpClient.create_auth_session(str(settings.bot.client_id), settings.bot.secret),
        asyncio.TaskGroup() as tg,
    ):
        tg.create_task(bot.connect())


if __name__ == "__main__":
    asyncio.run(main())

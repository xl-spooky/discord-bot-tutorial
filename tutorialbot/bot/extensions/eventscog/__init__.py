from disnake.ext import commands
from loguru import logger
from tutorialbot.bot.extensions.eventscog.events import ReadyCog

# some people would rather do imports as `from .events import ReadyCog`
# that could potentially cause multiple issues, especially if bot being run on a vps and
# not locally, if you'd like in a next video me explaining why it's not recommended let 
# me know.


def setup(bot: commands.Bot) -> None:
    """Entry point for adding this Cog to the bot.

    Args
    ----
        bot (commands.Bot):
            The bot instance to which the ReadyCog will be added.
    """
    bot.add_cog(ReadyCog(bot))
    logger.info("ReadyCog has been succesfully initiated")
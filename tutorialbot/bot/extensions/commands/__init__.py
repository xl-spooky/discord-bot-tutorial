from disnake.ext import commands
from loguru import logger
from tutorialbot.bot.extensions.commands.interaction import InteractionCog
from tutorialbot.bot.extensions.commands.prefix import PrefixCog

# some people would rather do imports as `from .events import Interaction`
# that could potentially cause multiple issues, especially if bot being run on a vps and
# not locally, if you'd like in a next video me explaining why it's not recommended let 
# me know.

def setup(bot: commands.Bot) -> None:
    """Entry point for adding this Cog to the bot.

    Args
    ----
        bot (commands.Bot):
            The bot instance to which the InteractionCog will be added.
    """
    bot.add_cog(InteractionCog(bot))
    logger.info("InteractionCog has been succesfully initiated")
    bot.add_cog(PrefixCog(bot))
    logger.info("PrefixCog has been succesfully initiated")
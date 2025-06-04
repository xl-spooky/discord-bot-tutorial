# This is an example cog in order how to create your first prefix command
# for furthermore details please join our discord servers and view our learning
# packages.

from disnake.ext import commands
from loguru import logger
from tutorialbot.bot import TutorialBot


class PrefixCog(commands.Cog):
    """A Cog that defines a prefix command.

    Provides a command '!ping' that responds with 'Pong!'.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the PrefixCog.

        Args
        ----
            bot (commands.Bot):
                The bot instance that this cog is attached to.
        """
        self.bot = bot

    @commands.command(
        name="ping",
        help="Responds with 'Pong!'"
    )
    async def ping(self, ctx: commands.Context[TutorialBot]) -> None:
        """Send back 'Pong!' in the channel where the command was invoked."""
        await ctx.send("Pong!")
        logger.info(f"Handled prefix command ping by {ctx.author}")

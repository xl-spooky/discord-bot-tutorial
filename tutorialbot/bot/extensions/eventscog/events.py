from disnake.ext import commands
from loguru import logger


class ReadyCog(commands.Cog):
    """A Cog that logs a message when the bot has successfully connected to Discord."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the ReadyCog.

        Args
        ----
            bot (commands.Bot):
                The bot instance that this cog is attached to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Event listener triggered when the bot has connected to Discord and is ready.

        Logs an informational message indicating that the bot is now ready.
        """
        logger.info(f"{self.bot.user} is now ready and connected to Discord.")

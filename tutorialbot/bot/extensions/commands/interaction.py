# This is an example cog in order how to create your first interaction command
# for furthermore details please join our discord servers and view our learning
# packages.

import disnake
from disnake.ext import commands
from loguru import logger
from tutorialbot.bot import TutorialBot


class InteractionCog(commands.Cog):
    """A Cog that defines a slash command interaction.

    Provides a slash command '/hello' that responds with a greeting.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the InteractionCog.

        Args
        ----
            bot (commands.Bot):
                The bot instance that this cog is attached to.
        """
        self.bot = bot

    @commands.slash_command()
    async def hello(self, inter: disnake.ApplicationCommandInteraction[TutorialBot]) -> None:
        """Send back a simple greeting message to the user who invoked the command."""
        await inter.response.send_message(f"Hello, {inter.author.name}!")
        logger.info(f"Handled slash command /hello by {inter.author}")

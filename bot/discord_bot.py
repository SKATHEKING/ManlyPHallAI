"""Discord bot entry point for Manly P. Hall AI Bot."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from backend.config import DISCORD_COMMAND_PREFIX, DISCORD_GUILD_ID, DISCORD_TOKEN, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)


class ManlyHallBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=DISCORD_COMMAND_PREFIX, intents=intents)

    async def setup_hook(self) -> None:
        if DISCORD_GUILD_ID is not None:
            guild = discord.Object(id=DISCORD_GUILD_ID)
            await self.tree.sync(guild=guild)
            logger.info("Synced Discord commands to guild %s", DISCORD_GUILD_ID)
        else:
            await self.tree.sync()
            logger.info("Synced Discord commands globally")

    async def on_ready(self) -> None:
        if self.user is None:
            logger.info("Discord bot is ready")
            return
        logger.info("Logged in as %s (%s)", self.user, self.user.id)


bot = ManlyHallBot()


@bot.tree.command(name="ask", description="Ask the Manly P. Hall AI bot a question")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str) -> None:
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        "The Discord bot scaffold is ready, but the answer pipeline is not connected yet."
    )


@bot.tree.command(name="status", description="Check whether the bot is online")
async def status(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Manly P. Hall AI Bot is online.", ephemeral=True)


def main() -> None:
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set. Add it to .env before starting the bot.")

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()

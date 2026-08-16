"""
Discord bot for Manly P. Hall AI Bot.

Slash commands over the RAG system, using discord.py 2.0+.

Command list, setup steps and how this relates to the HTTP API:
docs/modules/bot/discord_bot.md
"""

from __future__ import annotations

import logging
import asyncio
import os
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from backend.indexing import ChromaStore
from backend.generation import answer_question
from backend.retrieval import retrieve_chunks

from dotenv import load_dotenv

# ============================================================================
# Configuration
# ============================================================================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # Optional: for faster sync
DISCORD_COMMAND_PREFIX = "!"

# Discord message limit is 2000 characters
MAX_MESSAGE_LENGTH = 1900


# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Discord Bot Class
# ============================================================================


class ManlyHallBot(commands.Bot):
    """
    Discord bot for Manly P. Hall AI.
    
    Features:
    - Slash commands for Q&A
    - Indexed knowledge base (books)
    - Async generation with Ollama
    - Proper error handling and timeouts
    """
    
    def __init__(self):
        """Initialize the Discord bot with intents and configuration."""
        # Enable message content intents if needed for prefix commands
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=DISCORD_COMMAND_PREFIX,
            intents=intents,
            help_command=None,  # Disable default help (we'll use slash commands)
        )
        
        # Initialize store (will be set in setup_hook)
        self.store: Optional[ChromaStore] = None
    
    async def setup_hook(self) -> None:
        """
        Setup hook called when bot starts.
        
        - Sync slash commands
        - Initialize the RAG store
        """
        logger.info("🚀 Setting up Discord bot...")
        
        # Initialize the RAG store
        try:
            self.store = ChromaStore()
            count = self.store.get_collection_size()
            logger.info(f"✓ Initialized store with {count} indexed chunks")
        except Exception as e:
            logger.error(f"✗ Failed to initialize store: {e}")
            raise
        
        # Sync slash commands with Discord
        if DISCORD_GUILD_ID:
            try:
                guild = discord.Object(id=int(DISCORD_GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"✓ Synced {len(synced)} commands to guild {DISCORD_GUILD_ID}")
            except Exception as e:
                logger.error(f"✗ Failed to sync commands to guild: {e}")
        else:
            synced = await self.tree.sync()
            logger.info(f"✓ Synced {len(synced)} commands globally (may take 1 hour to appear)")
    
    async def on_ready(self) -> None:
        """Called when bot connects to Discord."""
        if self.user:
            logger.info(f"✓ Logged in as {self.user} ({self.user.id})")
        else:
            logger.info("✓ Bot is ready")


# ============================================================================
# Bot Instance
# ============================================================================

bot = ManlyHallBot()


# ============================================================================
# Slash Commands
# ============================================================================


@bot.tree.command(
    name="ask",
    description="Ask Manly P. Hall AI a question about the indexed books"
)
@app_commands.describe(
    question="Your question (will be answered using indexed knowledge)",
    sources="Number of sources to retrieve (default 5)"
)
async def ask_command(
    interaction: discord.Interaction,
    question: str,
    sources: int = 5
) -> None:
    """
    Answer a question using the indexed knowledge base.
    
    This command:
    1. Shows "thinking..." indicator
    2. Retrieves relevant passages
    3. Generates an answer with Ollama
    4. Sends the answer with citations
    
    Args:
        interaction: Discord interaction object
        question: User's question
        sources: Number of sources to retrieve (1-20)
    """
    # Validate inputs
    if not question.strip():
        await interaction.response.send_message(
            "❌ Question cannot be empty",
            ephemeral=True
        )
        return
    
    if not 1 <= sources <= 20:
        await interaction.response.send_message(
            "❌ Sources must be between 1 and 20",
            ephemeral=True
        )
        return
    
    # Show thinking indicator
    await interaction.response.defer(thinking=True)
    
    try:
        if not bot.store:
            await interaction.followup.send(
                "❌ Bot is not ready. Try again in a moment."
            )
            return
        
        logger.info(f"Question from {interaction.user}: {question[:100]}")
        
        # Generate answer (this may take a while)
        # Use asyncio.to_thread to prevent blocking
        result = await asyncio.to_thread(
            answer_question,
            question,
            bot.store,
            sources,
        )
        
        # Format response
        response = f"**Question:** {question}\n\n"
        response += f"**Answer:**\n{result.text}\n\n"
        
        if result.citations:
            response += "**Sources:**\n"
            for citation in result.citations[:5]:  # Limit to 5 citations
                response += f"• {citation}\n"
        
        response += f"\n*Confidence: {result.confidence:.0%}*"
        
        # Split into chunks if too long (Discord 2000 char limit)
        if len(response) > MAX_MESSAGE_LENGTH:
            # Send main answer first
            main_response = response[:MAX_MESSAGE_LENGTH]
            await interaction.followup.send(main_response)
            
            # Send continuation
            continuation = response[MAX_MESSAGE_LENGTH:]
            chunks = [continuation[i:i+MAX_MESSAGE_LENGTH] 
                     for i in range(0, len(continuation), MAX_MESSAGE_LENGTH)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(response)
        
        logger.info(f"✓ Answered question with {len(result.citations)} sources")
        
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        await interaction.followup.send(
            f"❌ Failed to generate answer: {str(e)[:100]}"
        )


@bot.tree.command(
    name="status",
    description="Check bot status and knowledge base statistics"
)
async def status_command(interaction: discord.Interaction) -> None:
    """
    Show bot status and index statistics.
    
    Displays:
    - Bot online status
    - Number of indexed chunks
    - Approximate knowledge coverage
    """
    try:
        if not bot.store:
            await interaction.response.send_message(
                "⚠️ Bot is initializing. Try again in a moment.",
                ephemeral=True
            )
            return
        
        count = bot.store.get_collection_size()
        
        response = (
            "✅ **Manly P. Hall AI Bot Status**\n"
            f"Status: Online\n"
            f"Indexed chunks: {count}\n"
            f"Mode: RAG (Retrieval-Augmented Generation)\n"
            f"Model: Ollama Llama 2\n"
            f"\n*Use `/ask` to ask a question*"
        )
        
        await interaction.response.send_message(response, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        await interaction.response.send_message(
            f"❌ Status check failed: {str(e)[:100]}",
            ephemeral=True
        )


@bot.tree.command(
    name="search",
    description="Search the knowledge base for a topic"
)
@app_commands.describe(
    query="Search query (will retrieve top passages)",
    results="Number of results (default 3)"
)
async def search_command(
    interaction: discord.Interaction,
    query: str,
    results: int = 3
) -> None:
    """
    Search the knowledge base without generating an answer.
    
    Returns top passages matching the query.
    
    Args:
        interaction: Discord interaction object
        query: Search query
        results: Number of passages to return (1-10)
    """
    if not query.strip():
        await interaction.response.send_message(
            "❌ Query cannot be empty",
            ephemeral=True
        )
        return
    
    if not 1 <= results <= 10:
        await interaction.response.send_message(
            "❌ Results must be between 1 and 10",
            ephemeral=True
        )
        return
    
    await interaction.response.defer(thinking=True)
    
    try:
        if not bot.store:
            await interaction.followup.send("❌ Bot is not ready.")
            return
        
        logger.info(f"Search from {interaction.user}: {query}")
        
        # Retrieve passages
        retrieved = await asyncio.to_thread(
            retrieve_chunks,
            query,
            bot.store,
            results,
        )
        
        if not retrieved:
            await interaction.followup.send(
                f"❌ No relevant passages found for: {query}"
            )
            return
        
        # Format results
        response = f"**Search Results for:** {query}\n\n"
        
        for i, chunk in enumerate(retrieved, 1):
            preview = chunk["text"][:150].replace("\n", " ")
            response += f"**[{i}]** (Score: {chunk['score']:.0%})\n"
            response += f"{preview}...\n"
            response += f"*Source: {chunk['source']}*\n\n"
        
        if len(response) > MAX_MESSAGE_LENGTH:
            response = response[:MAX_MESSAGE_LENGTH] + "..."
        
        await interaction.followup.send(response)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        await interaction.followup.send(f"❌ Search failed: {str(e)[:100]}")


@bot.tree.command(
    name="help",
    description="Show available commands and how to use them"
)
async def help_command(interaction: discord.Interaction) -> None:
    """
    Show help information about available commands.
    """
    help_text = (
        "**Manly P. Hall AI Bot - Help**\n\n"
        "**Commands:**\n"
        "`/ask <question>` - Ask a question about the indexed books\n"
        "`/search <query>` - Search for relevant passages\n"
        "`/status` - Check bot status and statistics\n"
        "`/help` - Show this help message\n\n"
        "**How it works:**\n"
        "1. Ask a question using `/ask`\n"
        "2. The bot searches the indexed knowledge base\n"
        "3. An AI generates an answer based on the passages\n"
        "4. The answer is returned with citations\n\n"
        "**Tips:**\n"
        "• Be specific in your questions\n"
        "• The bot uses semantic search - similar meanings work\n"
        "• Sources are listed for verification\n"
    )
    
    await interaction.response.send_message(help_text, ephemeral=True)


# ============================================================================
# Event Handlers
# ============================================================================


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """
    Handle errors in slash commands.
    """
    logger.error(f"Command error: {error}")
    
    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)[:100]}",
            ephemeral=True
        )


@bot.event
async def on_error(event, *args, **kwargs) -> None:
    """
    Handle errors in event listeners.
    """
    logger.error(f"Error in {event}", exc_info=True)


# ============================================================================
# Main Entry Point
# ============================================================================


def main() -> None:
    """
    Main entry point for Discord bot.
    
    Raises:
        SystemExit: If DISCORD_TOKEN is not set
    """
    if not DISCORD_TOKEN:
        raise SystemExit(
            "❌ DISCORD_TOKEN environment variable is not set.\n"
            "Add it to .env file or set it before running the bot."
        )
    
    logger.info("🚀 Starting Discord bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()

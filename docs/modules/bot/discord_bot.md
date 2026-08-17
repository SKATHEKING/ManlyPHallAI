# `bot/discord_bot.py` — Discord interface

Design notes extracted from the module's docstrings. Provides Discord slash
commands for the RAG system (Phase 1e), using discord.py 2.0+.

## Commands

- `/ask` — Answer questions using indexed books
- `/status` — Check bot status and index statistics
- `/search` — Show matching passages without generating an answer
- `/help` — List available commands

## Setup

1. Create a Discord application and get the token
2. Set the `DISCORD_TOKEN` environment variable
3. Run: `python -m bot.discord_bot`

Alternatively, run via script:

```bash
python scripts/run_discord_bot.py
```

## Relationship to the HTTP API

The bot imports the backend directly rather than calling the API over HTTP. That
avoids a network hop and a second service to deploy, but it means store
initialisation, the ask pipeline and answer formatting exist here as well as in
`backend/api/routes.py`, and the two copies have drifted — different bullet
characters, different confidence formatting, and a citation cap that only the bot
applies.

## Message limits

Discord caps a single message at 2000 characters, so long answers are split
before sending.

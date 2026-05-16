# Getting Started with Phase 1 Development

## Quick Project Structure

```
ManlyPHallAI/
├── backend/                    # Python support backend
│   ├── config.py              # ✓ Configuration (ready)
│   ├── main.py                # ✓ FastAPI support app (ready)
│   ├── ingestion/             # Phase 1b: Parsers & chunking
│   ├── indexing/              # Phase 1c: Embeddings & vector store
│   ├── retrieval/             # Phase 1d: Vector search
│   ├── generation/            # Phase 1d: LLM integration
│   └── api/                   # Phase 1e: Support endpoints
│
├── bot/
│   ├── __init__.py            # Discord bot package
│   └── discord_bot.py         # Discord bot entry point
│
├── frontend/
│   └── web/                   # Optional legacy demo UI
│       ├── index.html         # HTML interface
│       └── app.js             # JavaScript client
│
├── data/                      # Data storage
│   ├── books/                 # Book files go here
│   ├── chroma_db/             # Vector index
│   └── models/                # Cached models
│
├── scripts/                   # Utility scripts
│   ├── download_embeddings_model.py
│   ├── ingest_book.py
│   └── test_*.py
│
├── requirements.txt           # ✓ Dependencies
├── ARCHITECTURE.md            # ✓ System design
├── IMPLEMENTATION_GUIDE.md    # ✓ Build instructions
├── DECISIONS.md               # ✓ Design rationale
└── PROJECT_EVOLUTION.md       # ✓ Learning log
```

## Zero Cost Setup

ManlyPHallAI is **completely free and open-source**. No API keys, no paid services, no cloud costs required.

### What You Need
- **Python 3.10+** (free)
- **~2GB disk space** for embeddings model
- **~8GB RAM** for local Llama model
- Any modern laptop/desktop (Windows, macOS, Linux)

### Free Tools
All dependencies are open-source:
- **Ollama** — Local LLM engine (free, MIT licensed)
- **Chroma** — Vector database (free, Apache 2.0)
- **sentence-transformers** — Embeddings (free, Apache 2.0)
- **LangChain** — Text processing (free, MIT)
- **Discord.py** — Discord integration (free, MIT)
- **FastAPI** — API framework (free, BSD)

### No Paid Services
- ✓ No LLM API costs (uses local Ollama)
- ✓ No cloud hosting required (runs on your machine)
- ✓ No database subscriptions (Chroma is local)
- ✓ No API keys or credentials (except Discord bot token)

### Cost Projection
**Phase 1**: $0/month (your hardware only)
**Phases 2–5**: $0/month if self-hosted; €3–10/mo if cloud-hosted later (Hetzner VPS, AWS free tier)

See [DECISIONS.md](DECISIONS.md) for cost-benefit analysis and migration paths.

## Next Steps

### Phase 1 Setup (Complete RAG Pipeline)

#### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Download Embeddings Model
```bash
python scripts/download_embeddings_model.py
```

#### 4. Start Ollama Service
In a separate terminal:
```bash
ollama serve
ollama pull llama2:7b  # Or your preferred model
```

#### 5. Ingest Your First Book
```bash
python scripts/ingest_book.py data/books/your_book.pdf
```

#### 6. Test the System
```bash
# Run all tests
python scripts/test_ingestion.py
python scripts/test_indexing.py
python scripts/test_retrieval_generation.py
```

---

### Running the System

#### Option A: Start the HTTP API Server
```bash
python scripts/run_api.py
```

Then visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

Example API call:
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is enlightenment?"}'
```

#### Option B: Start the Discord Bot
```bash
# First, set your Discord token
export DISCORD_TOKEN="your-bot-token-here"

# Then run the bot
python scripts/run_discord_bot.py
```

Commands:
- `/ask <question>` — Answer a question
- `/search <query>` — Search for passages
- `/status` — Check bot status
- `/help` — Show available commands

#### Option C: Run Both (Recommended)
```bash
# Terminal 1: Ollama service
ollama serve

# Terminal 2: HTTP API
python scripts/run_api.py

# Terminal 3: Discord bot
export DISCORD_TOKEN="..."
python scripts/run_discord_bot.py
```

---

### Configuration

Create a `.env` file in the project root:
```bash
# Discord Bot
DISCORD_TOKEN=your-bot-token-here
DISCORD_GUILD_ID=your-guild-id  # Optional: for faster command sync

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# LLM Configuration
OLLAMA_MODEL=llama2:7b
```

See [backend/config.py](backend/config.py) for all available settings.

---

### Workflow Example

1. **Add books to knowledge base**
   ```bash
   python scripts/ingest_book.py data/books/book1.pdf
   python scripts/ingest_book.py data/books/book2.epub
   ```

2. **Ask questions via API**
   ```bash
   POST /api/ask {"question": "What is enlightenment?"}
   ```

3. **Or via Discord**
   ```
   /ask What is the law of correspondence?
   ```

4. **Get back answers with citations**
   ```
   Answer: [Generated answer based on retrieved passages]
   Sources:
   - book1.pdf, page 42
   - book2.epub, Chapter 3
   Confidence: 85%
   ```

---

### Troubleshooting

**Q: "ModuleNotFoundError: No module named 'backend'"**
- Make sure you're in the project root directory
- Use `PYTHONPATH=. python script.py`

**Q: "Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve` (in another terminal)
- Check it's on http://localhost:11434

**Q: Discord bot doesn't respond**
- Verify DISCORD_TOKEN is set correctly
- Check bot has message permissions in Discord
- Watch terminal for error messages

**Q: API returns 500 errors**
- Check logs for detailed error messages
- Verify ChromaStore is initialized
- Ensure Ollama is running

---

## Documentation Reference

- 📖 **[ARCHITECTURE.md](ARCHITECTURE.md)** — Understand the system design
- 🛠️ **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** — Detailed build instructions
- 🤔 **[DECISIONS.md](DECISIONS.md)** — Learn the "why" behind choices
- 📊 **[PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md)** — Track progress and learnings

---

**Ready to run? Start with the setup steps above!**

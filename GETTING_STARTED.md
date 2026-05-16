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

## Next Steps

### Follow Phase 1a (Foundations) from IMPLEMENTATION_GUIDE.md:

1. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Models**
   ```bash
   python scripts/download_embeddings_model.py
   ```

4. **Configure Discord**
   ```bash
   cp .env.example .env
   ```
   Add your bot token and guild ID to `.env`.

5. **Start Ollama** (in separate terminal)
   ```bash
   ollama serve
   ollama pull llama2:7b
   ```

6. **Run the Discord Bot**
   ```bash
   python scripts/run_discord_bot.py
   ```

### Then Proceed to Phase 1b, 1c, etc.

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for complete step-by-step instructions.

## Documentation Reference

- 📖 **[ARCHITECTURE.md](ARCHITECTURE.md)** — Understand the system design
- 🛠️ **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** — Follow to build Phase 1
- 🤔 **[DECISIONS.md](DECISIONS.md)** — Learn the "why" behind choices
- 📊 **[PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md)** — Track progress and learnings

## Quick Commands

```bash
# Verify installation
python -c "import fastapi; import chromadb; import discord; print('✓ Dependencies OK')"

# Check support API health
curl http://localhost:8000/health

# View project structure
tree -L 3 -I '__pycache__|*.pyc'
```

---

**Ready to build? Start with Phase 1a in [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)!**

# Resources and Implementation Guide

This document provides curated resources, documentation links, and step-by-step setup instructions for every technology listed in `technologies.md`. The goal is to make learning and implementation practical and gradual, so you can understand each tool as you use it.

## Prerequisites and Foundation

Before diving into specific technologies, familiarize yourself with these fundamentals:

### Python
- **Official Site:** https://www.python.org/
- **Learn:** https://docs.python.org/3/tutorial/
- **Best Practice:** Use Python 3.10 or later.
- **Setup:**
  1. Install Python from python.org or use a version manager like `pyenv`.
  2. Create a virtual environment: `python -m venv venv` and activate it.
  3. Use `pip` to install packages: `pip install -r requirements.txt`.

### Git and Version Control
- **Official Site:** https://git-scm.com/
- **Learn:** https://git-scm.com/book/en/v2
- **Setup:**
  1. Install Git.
  2. Initialize your project: `git init`.
  3. Create a `.gitignore` file to exclude sensitive and temporary files.

### Virtual Environments
- **Learn:** https://docs.python.org/3/tutorial/venv.html
- **Why:** Keeps dependencies isolated per project.
- **Setup:**
  ```
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  # or
  venv\Scripts\activate  # Windows
  ```

---

## Phase 1: Book-Based Knowledge Engine

### FastAPI

**What it is:** A lightweight, modern Python framework for building APIs.

**Official Resources:**
- Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

**Step-by-Step Setup:**
1. Install: `pip install fastapi uvicorn`
2. Create a `main.py` file with a simple endpoint.
3. Run: `uvicorn main.py:app --reload`
4. Visit `http://localhost:8000/docs` to see the auto-generated API documentation.

**First Implementation:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Manly P. Hall AI Bot"}

@app.post("/ask")
def ask_question(question: str):
    # Placeholder: later will call retrieval + generation
    return {"question": question, "answer": "To be implemented"}
```

**Learning Path:**
1. Build a simple endpoint that echoes input.
2. Add request/response models using Pydantic.
3. Add error handling.
4. Connect to your database layer.

---

### PDF, EPUB, and Text Parsing

**What it is:** Libraries that extract and parse content from different file formats.

**Recommended Libraries:**

#### PyPDF2 (for PDFs)
- Docs: https://pypdf2.readthedocs.io/
- Install: `pip install pypdf2`
- Use case: Extract text from PDFs.

#### python-docx (for Word documents)
- Docs: https://python-docx.readthedocs.io/
- Install: `pip install python-docx`

#### Calibre (for EPUB)
- Docs: https://calibre-ebook.com/
- Install: Can be installed via package managers or directly from the site.
- Python wrapper: `pip install ebooklib`

#### Pypub (for EPUB parsing)
- Install: `pip install pypub`

**Step-by-Step Implementation:**
1. Start with plain text files: read with Python's built-in file operations.
2. Move to PDFs: use PyPDF2 to extract pages.
3. Add metadata tracking: store book title, author, chapter info.
4. Build an ingestion pipeline that standardizes the output.

**First Script:**
```python
from PyPDF2 import PdfReader

def extract_pdf_text(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Usage
pdf_text = extract_pdf_text("source_book.pdf")
print(pdf_text[:500])  # Print first 500 chars
```

---

### Text Chunking and Tokenization

**What it is:** Breaking long documents into smaller pieces that are easier to search and embed.

**Recommended Libraries:**

#### LangChain (Text Splitting)
- Docs: https://python.langchain.com/docs/modules/data_connection/document_loaders/
- Install: `pip install langchain`
- Why: Provides multiple splitting strategies (character, token, recursive).

#### tiktoken (OpenAI Tokenizer)
- Docs: https://github.com/openai/tiktoken
- Install: `pip install tiktoken`
- Use: Understand token counts for your chosen LLM.

#### Sentence-Transformers
- Docs: https://www.sbert.net/
- Install: `pip install sentence-transformers`

**Step-by-Step Implementation:**
1. Start with simple character-based splitting (e.g., split by "\n\n").
2. Move to token-based splitting using tiktoken.
3. Add overlap between chunks so context is not lost at boundaries.
4. Track chunk metadata (source, page, order).

**First Script:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text, chunk_size=300, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks = splitter.split_text(text)
    return chunks

# Usage
chunks = chunk_text(pdf_text)
print(f"Number of chunks: {len(chunks)}")
print(f"First chunk: {chunks[0][:200]}")
```

---

### Embeddings

**What it is:** Converting text into numerical vectors so the system can find similar content.

**Recommended Services:**

#### OpenAI Embeddings
- Docs: https://platform.openai.com/docs/guides/embeddings
- Model: `text-embedding-3-small` (efficient and good quality).
- Cost: ~$0.02 per million tokens.
- Install: `pip install openai`

#### Hugging Face Sentence-Transformers
- Docs: https://www.sbert.net/
- Model: `all-MiniLM-L6-v2` (free, runs locally).
- Install: `pip install sentence-transformers`

#### Cohere
- Docs: https://docs.cohere.com/reference/embed
- Model: `embed-english-v3.0` (high quality).

**Step-by-Step Implementation:**
1. Start with a free local model like `all-MiniLM-L6-v2`.
2. Generate embeddings for your first small book set.
3. Store embeddings in memory or a simple format.
4. Test retrieval quality (is similar content retrieved?).
5. Upgrade to a better model if quality is insufficient.

**First Script:**
```python
from sentence_transformers import SentenceTransformer

# Load a local model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for your chunks
chunks = ["chunk 1 text here", "chunk 2 text here"]
embeddings = model.encode(chunks)

print(f"Embedding shape: {embeddings.shape}")
print(f"First embedding (first 10 values): {embeddings[0][:10]}")
```

---

### Vector Databases

**What it is:** A database optimized for storing and searching embeddings.

**Recommended Options:**

#### PostgreSQL with pgvector (for learning and small projects)
- Docs: https://github.com/pgvector/pgvector
- Why: Free, local, full-featured.
- Setup: https://github.com/pgvector/pgvector#installation

#### Pinecone (managed, cloud-hosted)
- Docs: https://docs.pinecone.io/
- Why: Simplest to get started with.
- Free tier: Yes, with rate limits.
- Install: `pip install pinecone-client`

#### Weaviate (open-source, self-hosted or cloud)
- Docs: https://weaviate.io/developers/weaviate
- Install: Available as Docker container or Python library.

#### Chroma (lightweight, local)
- Docs: https://docs.trychroma.com/
- Install: `pip install chromadb`
- Why: Perfect for prototyping without external services.

**Step-by-Step Implementation:**
1. Start with Chroma for local prototyping (no setup required).
2. Test ingestion and retrieval with a small dataset.
3. Move to PostgreSQL with pgvector for production-like persistence.
4. Upgrade to managed services only if scaling requires it.

**First Script (using Chroma):**
```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize Chroma
client = chromadb.Client()
collection = client.create_collection(name="books")

# Embed and store
model = SentenceTransformer('all-MiniLM-L6-v2')
chunks = ["Esoteric wisdom involves deep spiritual knowledge", "Occultism studies hidden forces"]
embeddings = model.encode(chunks).tolist()

# Add to collection
collection.add(
    ids=["chunk_1", "chunk_2"],
    embeddings=embeddings,
    documents=chunks,
    metadatas=[{"source": "book1"}, {"source": "book2"}]
)

# Query
results = collection.query(
    query_embeddings=model.encode(["spiritual knowledge"]).tolist(),
    n_results=2
)
print(results)
```

---

### PostgreSQL

**What it is:** A powerful, open-source relational database.

**Official Resources:**
- Docs: https://www.postgresql.org/docs/
- Installation: https://www.postgresql.org/download/
- Tutorial: https://www.postgresql.org/docs/current/tutorial.html

**Python Connection:**
- Install: `pip install psycopg2-binary sqlalchemy`
- Docs: https://www.sqlalchemy.org/

**Step-by-Step Setup:**
1. Install PostgreSQL on your machine.
2. Create a new database: `createdb manly_hall_bot`
3. Create a Python connection script.
4. Define your data schema (books, chunks, metadata, sources).
5. Test CRUD operations (Create, Read, Update, Delete).

**First Script:**
```python
import psycopg2

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="manly_hall_bot",
    user="your_user",
    password="your_password"
)

cur = conn.cursor()

# Create a simple table
cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        author VARCHAR(255),
        ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()
cur.close()
conn.close()

print("Database setup complete")
```

---

### LLM Providers

**What it is:** APIs that provide language models for generating answers.

**Recommended Options:**

#### OpenAI
- Docs: https://platform.openai.com/docs
- Model: `gpt-4-turbo` (best quality) or `gpt-3.5-turbo` (faster, cheaper).
- Install: `pip install openai`
- Cost: Variable based on tokens.

#### Anthropic Claude
- Docs: https://docs.anthropic.com/
- Model: `claude-3-sonnet-20240229` (good balance).
- Install: `pip install anthropic`

#### Open-source: Ollama or Local LLaMA
- Ollama: https://ollama.ai/
- Why: Free, runs locally, no API costs.
- Models: Llama 2, Mistral, Neural Chat.

**Step-by-Step Implementation:**
1. Start with a free local model like Ollama to understand the integration.
2. Test basic prompt engineering without API costs.
3. Switch to OpenAI or Claude once you understand the workflow.
4. Optimize prompts for grounding and citation.

**First Script (using OpenAI):**
```python
from openai import OpenAI

client = OpenAI(api_key="your_api_key")

def generate_answer(question, context):
    prompt = f"""
    Answer this question based ONLY on the provided context.
    If the context does not support an answer, say "I don't know."
    
    Question: {question}
    Context: {context}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Usage
answer = generate_answer(
    "What is esotericism?",
    "Esotericism is the study of hidden or esoteric knowledge..."
)
print(answer)
```

---

## Phase 2: Grounding and Quality Control

### Prompt Templates and Management

**What it is:** Structured ways to define and organize prompts for consistency and testing.

**Recommended Approaches:**

#### LangChain Prompts
- Docs: https://python.langchain.com/docs/modules/model_io/prompts/
- Install: Already installed if you have LangChain.

#### Jinja2 Templates
- Docs: https://jinja.palletsprojects.com/
- Install: `pip install jinja2`

**Step-by-Step Implementation:**
1. Start with simple Python f-strings.
2. Move to Jinja2 templates for complex prompts.
3. Create a prompt library that you version control.
4. Test prompt variations using your evaluation set.

**First Script:**
```python
from jinja2 import Template

prompt_template = Template("""
You are a knowledgeable assistant about esotericism and Manly P. Hall.
Answer the following question based ONLY on the provided sources.

Question: {{ question }}

Sources:
{% for source in sources %}
- {{ source }}
{% endfor %}

If you cannot answer from the sources, say "I don't have enough information to answer this."

Answer:
""")

def render_prompt(question, sources):
    return prompt_template.render(question=question, sources=sources)

# Usage
prompt = render_prompt(
    "What is the hermetic principle?",
    ["Source 1: The Hermetic Principles are seven core teachings...", "Source 2: ..."]
)
print(prompt)
```

### Evaluation Frameworks

**What it is:** Tools and methodologies to measure answer quality.

**Recommended Approaches:**

#### Manual Evaluation
- Create a spreadsheet or JSON file with test questions and expected answers.
- Score responses on correctness, citation quality, and clarity.

#### RAGAS (Retrieval-Augmented Generation Assessment)
- Docs: https://github.com/explodinggradients/ragas
- Install: `pip install ragas`
- Metrics: measures faithfulness, relevance, and factuality.

#### DeepEval
- Docs: https://github.com/confident-ai/deepeval
- Install: `pip install deepeval`

**Step-by-Step Implementation:**
1. Create a simple JSON file with 10-20 test questions and reference answers.
2. Manually run the bot against these questions and score the responses.
3. Track scores over time as you improve the prompt and retrieval.
4. Use RAGAS or DeepEval once the basic workflow is stable.

**First Script:**
```python
import json

# Define test cases
test_cases = [
    {
        "question": "What is Manly P. Hall known for?",
        "expected_keywords": ["esoteric", "author", "philosopher"],
        "expected_sources": ["biography", "works"]
    },
    {
        "question": "What are the Hermetic Principles?",
        "expected_keywords": ["seven", "principles", "universal"],
        "expected_sources": ["Hermetics", "ancient wisdom"]
    }
]

# Save to file
with open("test_cases.json", "w") as f:
    json.dump(test_cases, f, indent=2)

# Simple scoring
def score_answer(answer, expected_keywords):
    score = 0
    for keyword in expected_keywords:
        if keyword.lower() in answer.lower():
            score += 1
    return score / len(expected_keywords)

# Usage
answer = "Manly P. Hall was an esoteric author and philosopher..."
score = score_answer(answer, ["esoteric", "author", "philosopher"])
print(f"Score: {score:.2%}")
```

---

## Phase 3: Internet-Augmented Research

### Search APIs

**What it is:** Services that let you query the internet from your code.

**Recommended Options:**

#### Brave Search API
- Docs: https://api.search.brave.com/
- Why: Privacy-focused, good quality results.
- Pricing: Free tier available.
- Install: `pip install requests`

#### Tavily Search
- Docs: https://tavily.com/
- Why: Designed for AI agents.
- Free tier: Yes.

#### Google Custom Search API
- Docs: https://developers.google.com/custom-search/v1/overview
- Why: Familiar, reliable.
- Cost: $5 per 1000 queries after free tier.

#### SerpAPI
- Docs: https://serpapi.com/docs
- Why: Easy to use, supports many search engines.
- Pricing: Free trial, then paid.

**Step-by-Step Implementation:**
1. Choose one search API.
2. Get an API key.
3. Test basic queries.
4. Integrate results into your retrieval system.
5. Add source ranking and deduplication.

**First Script (using SerpAPI):**
```python
from serpapi import GoogleSearch

def search_online(query, num_results=5):
    params = {
        "q": query,
        "api_key": "your_serpapi_key",
        "num": num_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    formatted_results = []
    if "organic_results" in results:
        for result in results["organic_results"][:num_results]:
            formatted_results.append({
                "title": result.get("title"),
                "url": result.get("link"),
                "snippet": result.get("snippet")
            })
    
    return formatted_results

# Usage
results = search_online("Manly P. Hall esoteric philosophy", num_results=3)
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}\n")
```

### Web Scraping and Readability

**What it is:** Extracting and parsing content from web pages.

**Recommended Libraries:**

#### BeautifulSoup
- Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Install: `pip install beautifulsoup4`

#### Readability
- Install: `pip install readability-lxml`
- Why: Extracts the main article content, skipping ads and clutter.

#### Selenium (for JavaScript-heavy sites)
- Docs: https://selenium-python.readthedocs.io/
- Install: `pip install selenium`

**Step-by-Step Implementation:**
1. Use BeautifulSoup for static HTML content.
2. Extract text, links, and structure.
3. Use Readability to isolate main content.
4. Store URL, timestamp, and trust score in metadata.
5. Deduplicate against existing book content.

**First Script:**
```python
from bs4 import BeautifulSoup
import requests

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    title = soup.find('h1')
    
    # Extract paragraphs
    paragraphs = soup.find_all('p')
    text = " ".join([p.get_text() for p in paragraphs])
    
    return {
        "title": title.get_text() if title else "Unknown",
        "url": url,
        "content": text[:500]  # First 500 chars
    }

# Usage
page_data = scrape_page("https://example-esoteric-site.com/article")
print(page_data)
```

### Source Ranking and Filtering

**What it is:** Evaluating web sources for quality and trustworthiness.

**Approach:**

#### Manual Source Curation
- Maintain a whitelist of approved domains.
- Research sources before inclusion.

#### Domain Authority Scoring
- Install: `pip install requests`
- Use APIs like Moz or Ahrefs to check domain authority.

#### Content Filtering
- Check for misinformation markers.
- Filter by language, publication date, and source type.

**First Script:**
```python
# Simple domain whitelist
TRUSTED_DOMAINS = [
    "example-esoteric.com",
    "academic-site.edu",
    "manly-p-hall-foundation.org"
]

def is_trusted_source(url):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    # Remove 'www.' prefix
    domain = domain.replace('www.', '')
    return domain in TRUSTED_DOMAINS

# Usage
print(is_trusted_source("https://www.example-esoteric.com/article"))  # True
print(is_trusted_source("https://untrusted-site.com/article"))  # False
```

---

## Phase 4: Audiovisual Experience

### Text-to-Speech (TTS)

**What it is:** Converting text to spoken audio.

**Recommended Services:**

#### ElevenLabs
- Docs: https://elevenlabs.io/docs
- Why: High-quality, natural-sounding voices.
- Pricing: Free tier available.
- Install: `pip install elevenlabs`

#### OpenAI TTS
- Docs: https://platform.openai.com/docs/guides/text-to-speech
- Models: `tts-1` (fast) or `tts-1-hd` (higher quality).
- Install: Already have OpenAI library.

#### Azure Text-to-Speech
- Docs: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/text-to-speech
- Install: `pip install azure-cognitiveservices-speech`

#### Google Cloud Text-to-Speech
- Docs: https://cloud.google.com/text-to-speech/docs
- Install: `pip install google-cloud-texttospeech`

#### Amazon Polly
- Docs: https://docs.aws.amazon.com/polly/
- Install: `pip install boto3`

**Step-by-Step Implementation:**
1. Start with a free tier service (OpenAI or ElevenLabs).
2. Generate audio for a sample answer.
3. Store the audio file locally or in object storage.
4. Test playback in your frontend.
5. Measure latency and quality.

**First Script (using ElevenLabs):**
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your_api_key")

def generate_speech(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    audio = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_monolingual_v1"
    )
    return audio

# Usage
answer = "Manly P. Hall was a prominent esoteric philosopher..."
audio = generate_speech(answer)

# Save to file
with open("answer.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### Avatar or Talking Image Services

**What it is:** AI-generated video of a speaking person (head and shoulders, typically).

**Recommended Services:**

#### D-ID
- Docs: https://www.d-id.com/
- Why: Good quality, easy API.
- Pricing: Free tier available.
- Install: `pip install requests`

#### HeyGen
- Docs: https://docs.heygen.com/
- Why: High realism, many customization options.
- Pricing: Paid, but very polished.

#### Synthesia
- Docs: https://www.synthesia.io/
- Why: Enterprise-grade, professional.
- Pricing: Paid.

#### Custom (open-source)
- DeepFaceLive: https://github.com/iperov/DeepFaceLive
- OpenFace: https://github.com/TadasBaltrusaitis/OpenFace

**Step-by-Step Implementation:**
1. Start with a hosted service like D-ID for speed.
2. Provide a portrait image of your avatar.
3. Send text or audio to generate the talking video.
4. Integrate the video URL into your frontend.
5. Sync playback with the bot's text response.

**First Script (using D-ID):**
```python
import requests
import json

def generate_talking_video(text, portrait_url):
    api_key = "your_d_id_api_key"
    url = "https://api.d-id.com/talks"
    
    payload = {
        "source_url": portrait_url,
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "elevenlabs",
                "voice_id": "21m00Tcm4TlvDq8ikWAM"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Usage
video = generate_talking_video(
    "Welcome to the Manly P. Hall AI Assistant",
    "https://example.com/portrait.jpg"
)
print(video)
```

### Frontend State Management and Synchronization

**What it is:** Coordinating text, audio, and video playback in the UI.

**Recommended Approaches:**

#### React with Hooks
- Docs: https://react.dev/
- Library: `react` and `react-dom`
- State management: use `useState` and `useEffect`

#### Zustand (lightweight state management)
- Docs: https://github.com/pmndrs/zustand
- Install: `npm install zustand`

**First Script (React example):**
```jsx
import React, { useState, useEffect } from 'react';

function ChatBot() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async () => {
    setIsLoading(true);
    
    // Call backend to get answer
    const response = await fetch('/api/ask', {
      method: 'POST',
      body: JSON.stringify({ question })
    });
    
    const data = await response.json();
    setAnswer(data.answer);
    setAudioUrl(data.audio_url);
    setVideoUrl(data.video_url);
    setIsLoading(false);
  };

  return (
    <div>
      <input 
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about esotericism..."
      />
      <button onClick={handleAsk} disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Ask'}
      </button>
      
      {answer && <p>{answer}</p>}
      {audioUrl && <audio src={audioUrl} controls autoPlay />}
      {videoUrl && <video src={videoUrl} controls autoPlay />}
    </div>
  );
}

export default ChatBot;
```

---

## Phase 5: Iteration and Expansion

### Experiment Tracking and Prompt Versioning

**What it is:** Tracking changes to prompts and their effects on output quality.

**Recommended Tools:**

#### Weights & Biases
- Docs: https://docs.wandb.ai/
- Install: `pip install wandb`
- Why: Great for ML experiment tracking.

#### MLflow
- Docs: https://mlflow.org/
- Install: `pip install mlflow`

#### Simple Git-based approach
- Create a `prompts/` directory with versioned prompt files.
- Use Git to track changes.
- Add metadata (date, author, test results) to each version.

**Step-by-Step Implementation:**
1. Start with Git-based versioning.
2. Create a CSV file tracking prompt versions and their scores.
3. Move to a tool like Weights & Biases once you have many experiments.

---

### Monitoring and Analytics

**What it is:** Tracking system performance, latency, errors, and user satisfaction.

**Recommended Tools:**

#### Sentry (error tracking)
- Docs: https://docs.sentry.io/
- Install: `pip install sentry-sdk`
- Free tier: Yes.

#### Datadog or New Relic (APM)
- Docs: https://docs.datadoghq.com/ or https://docs.newrelic.com/
- Pricing: Paid, but trials available.

#### Prometheus + Grafana (open-source)
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Why: Free, self-hosted option.

#### Simple logging
- Use Python's built-in `logging` module.
- Log to files or a cloud service like LogRocket.

**First Script:**
```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="bot_activity.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def log_interaction(question, answer, latency, retrieval_score):
    logger.info(
        f"Question: {question} | "
        f"Answer: {answer[:100]}... | "
        f"Latency: {latency}ms | "
        f"Retrieval Score: {retrieval_score}"
    )

# Usage
log_interaction(
    "What is esotericism?",
    "Esotericism is the study of...",
    250,
    0.92
)
```

---

### Automated Testing and CI/CD

**What it is:** Testing code automatically before deployment.

**Recommended Tools:**

#### pytest
- Docs: https://docs.pytest.org/
- Install: `pip install pytest`

#### GitHub Actions (CI/CD)
- Docs: https://docs.github.com/en/actions
- Why: Free, integrated with GitHub.

#### Docker
- Docs: https://docs.docker.com/
- Install: https://www.docker.com/products/docker-desktop/
- Why: Reproducible environments.

**First Script (pytest example):**
```python
# test_bot.py
import pytest
from your_bot import ask_question

def test_simple_answer():
    answer = ask_question("What is esoteric?")
    assert answer is not None
    assert len(answer) > 0

def test_citation_exists():
    answer = ask_question("What is the Hermetic Principle?")
    assert "source" in answer.lower() or "[" in answer

def test_refusal_on_unknown():
    answer = ask_question("What is the capital of Mars?")
    assert "don't know" in answer.lower() or "uncertain" in answer.lower()

# Run: pytest test_bot.py
```

---

## Cross-Cutting: DevOps and Infrastructure

### Docker

**What it is:** Container technology that packages your app with all dependencies.

**Official Resources:**
- Docs: https://docs.docker.com/
- Tutorial: https://docs.docker.com/get-started/

**First Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t manly-hall-bot .
docker run -p 8000:8000 manly-hall-bot
```

### Cloud Hosting

#### Vercel (for Next.js frontend)
- Docs: https://vercel.com/docs
- Free tier: Yes.
- Deploy: Connect GitHub repo, auto-deploy on push.

#### Render, Railway, or Heroku (for FastAPI backend)
- Render: https://render.com/docs
- Railway: https://docs.railway.app/
- Heroku: https://devcenter.heroku.com/

#### AWS, Google Cloud, or Azure (for more control)
- AWS: https://docs.aws.amazon.com/
- GCP: https://cloud.google.com/docs
- Azure: https://docs.microsoft.com/en-us/azure/

### Environment Variables and Secrets

**What it is:** Safely storing API keys and configuration without committing them to Git.

**Recommended Approach:**

#### python-dotenv
- Install: `pip install python-dotenv`
- Create a `.env` file (never commit to Git).
- Load in Python: `from dotenv import load_dotenv; load_dotenv()`

**First Script:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
db_password = os.getenv("DB_PASSWORD")

# Use these variables safely
```

---

## Recommended Learning Path

If you're new to all these technologies, follow this sequence:

1. **Week 1-2: Fundamentals**
   - Python basics, virtual environments, Git
   - Simple FastAPI app

2. **Week 3-4: Data**
   - PDF/text parsing
   - Chunking and embeddings (start local)
   - Chroma for local vector storage

3. **Week 5-6: Retrieval and Generation**
   - PostgreSQL basics
   - LLM API (OpenAI or Claude)
   - Prompt engineering

4. **Week 7-8: Quality**
   - Evaluation frameworks
   - Simple testing with pytest
   - Logging and monitoring

5. **Week 9-10: Web**
   - Search APIs
   - Web scraping
   - Source filtering

6. **Week 11-12: Media**
   - TTS (ElevenLabs or OpenAI)
   - Avatar service (D-ID)
   - Frontend integration

7. **Week 13+: Polish and Deployment**
   - Docker
   - CI/CD
   - Cloud hosting
   - Ongoing iteration

---

## Quick Reference: Installation Commands

```bash
# Core
pip install python-dotenv git

# Phase 1
pip install fastapi uvicorn pypdf2 ebooklib python-docx
pip install langchain tiktoken sentence-transformers
pip install openai anthropic
pip install chromadb sqlalchemy psycopg2-binary

# Phase 2
pip install jinja2 ragas

# Phase 3
pip install requests beautifulsoup4 readability-lxml selenium

# Phase 4
pip install elevenlabs

# Phase 5
pip install pytest wandb sentry-sdk

# DevOps
pip install docker

# Frontend (npm)
npm install next react zustand
```

---

## Final Notes

- Start small: use free tiers and local tools first.
- Move to paid or cloud services only when you've proven the concept.
- Keep learning incremental: do not try to master all technologies at once.
- Reference these docs frequently as you build.
- Join communities: LangChain Discord, OpenAI community, etc.

Good luck building the Manly P. Hall AI Bot!

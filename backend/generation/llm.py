"""
LLM client for generating answers using Ollama.

This module provides Phase 1d (generation step):
1. Integrate with local Ollama LLM
2. Send prompts with retrieved context
3. Generate grounded answers citing sources

Main class: OllamaLLM (wrapper around Ollama)
Main function: generate_answer(prompt, retrieved_chunks) -> str

The LLM module is responsible for:
- Connecting to Ollama service
- Managing model loading/switching
- Generating answers grounded in retrieved chunks
- Handling streaming or batch responses

Example usage:
    from backend.generation.llm import OllamaLLM
    
    llm = OllamaLLM()
    answer = llm.generate(prompt, temperature=0.3)
    
    # Or use the high-level function:
    from backend.generation import generate_answer
    answer = generate_answer(prompt, retrieved_chunks)

Note: Requires Ollama service running locally:
    - Download from ollama.ai
    - Run: ollama pull llama2:7b (or other model)
    - Ollama service runs on http://localhost:11434/
"""

from __future__ import annotations

import logging
import requests
import json
from typing import Optional

from backend.config import get_settings


logger = logging.getLogger(__name__)


def _default_api_url() -> str:
    """
    Ollama API endpoint (local by default).

    Derived from settings.ollama_base_url rather than hardcoded, so the
    OLLAMA_BASE_URL / OLLAMA_URL environment variables that .env.example and
    docker-compose.yml already advertise finally take effect.
    """
    return f"{get_settings().ollama_base_url.rstrip('/')}/api"


class OllamaLLM:
    """
    Wrapper around Ollama LLM for generating answers.
    
    Ollama is a local LLM runtime that allows running models like Llama 2
    without cloud APIs. This wrapper:
    - Connects to Ollama service
    - Manages model lifecycle
    - Generates answers with configurable temperature
    
    Attributes:
        model: Model name (e.g., "llama2:7b")
        api_url: Ollama API base URL
        temperature: Sampling temperature (0-1, lower = more focused)
    """
    
    def __init__(
        self,
        model: str | None = None,
        api_url: str | None = None,
        temperature: float | None = None,
    ):
        """
        Initialize Ollama LLM client.
        
        Args:
            model: Model identifier (e.g., "llama2:7b", "mistral", etc.)
            api_url: Ollama API endpoint (default: localhost:11434)
            temperature: Sampling temperature (0.0-1.0)
                        0.0 = deterministic/focused
                        1.0 = creative/random
                        0.3 = good balance (default)
        """
        settings = get_settings()
        self.model = settings.ollama_model if model is None else model
        self.api_url = _default_api_url() if api_url is None else api_url
        self.temperature = settings.llm_temperature if temperature is None else temperature
        self._top_p = settings.llm_top_p
        self._top_k = settings.llm_top_k
        
        # Verify Ollama is running
        self._verify_ollama()
        
        logger.info(f"✓ Initialized OllamaLLM: {model}")
    
    def _verify_ollama(self):
        """
        Check if Ollama service is running.
        
        Raises:
            ConnectionError: If Ollama is not reachable
        """
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Ollama returned non-200 status")
            
            # Check if model is available
            available_models = response.json().get("models", [])
            model_names = [m["name"] for m in available_models]
            
            if self.model not in model_names:
                logger.warning(
                    f"⚠ Model {self.model} not available in Ollama.\n"
                    f"Available models: {model_names}\n"
                    f"Run: ollama pull {self.model}"
                )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"❌ Cannot connect to Ollama at {self.api_url}\n"
                f"Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            logger.warning(f"Could not verify Ollama: {e}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate an answer using Ollama.
        
        Sends the prompt to Ollama and gets a completion.
        This is a synchronous call (blocks until response received).
        
        Args:
            prompt: The prompt/question for the LLM
            max_tokens: Maximum tokens in response (default 512)
            temperature: Override default temperature if specified
            
        Returns:
            Generated answer text
            
        Raises:
            requests.exceptions.RequestException: If Ollama request fails
        """
        temp = temperature if temperature is not None else self.temperature
        
        try:
            logger.debug(f"Sending prompt to {self.model}...")
            
            # Ollama generate endpoint
            # Parameters:
            # - model: Which model to use
            # - prompt: Input prompt
            # - stream: False for batch mode (True for streaming)
            # - options: Temperature, num_predict (max tokens)
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,  # Batch mode
                    "options": {
                        "temperature": temp,
                        "num_predict": max_tokens,
                        "top_p": self._top_p,  # Nucleus sampling
                        "top_k": self._top_k,  # Top-k sampling
                    },
                },
                timeout=300,  # 5 minute timeout for long responses
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama returned status {response.status_code}: {response.text}")
            
            # Extract response text
            result = response.json()
            answer = result.get("response", "")
            
            logger.debug(f"Generated {len(answer)} characters")
            return answer
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise
    
    def generate_stream(self, prompt: str, temperature: Optional[float] = None):
        """
        Generate answer using streaming (for real-time response display).
        
        Yields chunks of text as they're generated. Useful for Discord
        where we want to show answer incrementally.
        
        Args:
            prompt: The prompt/question for the LLM
            temperature: Override default temperature if specified
            
        Yields:
            Text chunks as they're generated
        """
        temp = temperature if temperature is not None else self.temperature
        
        try:
            logger.debug(f"Starting stream generation with {self.model}...")
            
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,  # Streaming mode
                    "options": {
                        "temperature": temp,
                        "top_p": self._top_p,
                        "top_k": self._top_k,
                    },
                },
                timeout=300,
                stream=True,
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama returned status {response.status_code}")
            
            # Stream response line by line
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    text = chunk.get("response", "")
                    if text:
                        yield text
                        
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            raise
    
    def is_running(self) -> bool:
        """
        Check if Ollama service is reachable.
        
        Returns:
            True if Ollama is running, False otherwise
        """
        try:
            requests.get(f"{self.api_url}/tags", timeout=2)
            return True
        except:
            return False


def generate_answer(
    prompt: str,
    retrieved_chunks: list[dict],
    model: str | None = None,
) -> str:
    """
    High-level function to generate an answer from retrieved chunks.
    
    This function:
    1. Verifies retrieval results exist
    2. Initializes Ollama LLM
    3. Generates grounded answer
    4. Returns answer for display
    
    Args:
        prompt: The full prompt (should include context from chunks)
        retrieved_chunks: List of retrieved relevant chunks with sources
        model: Which model to use (default from config)
        
    Returns:
        Generated answer text
    """
    if not prompt:
        logger.error("Empty prompt provided to generate_answer")
        return "Error: No prompt provided"
    
    if not retrieved_chunks:
        logger.warning("No retrieved chunks provided for context")
    
    try:
        llm = OllamaLLM(model=model)
        answer = llm.generate(prompt)
        return answer
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        return f"Error generating answer: {str(e)}"


__all__ = ["OllamaLLM", "generate_answer"]

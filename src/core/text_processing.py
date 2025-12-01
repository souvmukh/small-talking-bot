import time
import hashlib
from functools import lru_cache
from typing import Optional, Dict, List, Tuple
from collections import OrderedDict
from pydantic import BaseModel, HttpUrl, Field
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logger import log

# ----------------------------
# 1. Pydantic Configuration Models
# ----------------------------


class LLMConfig(BaseModel):
    """
    A Pydantic model to hold and validate the configuration for the LLM.
    Using Pydantic ensures that the configuration is type-safe and valid
    before it's used by the application, preventing common errors.
    """

    model_name: str = "phi3:mini"  # model name
    base_url: HttpUrl = "http://localhost:11434"
    cache_size: int = Field(default=100, ge=0, description="Number of responses to cache. Set to 0 to disable caching.")
    timeout_seconds: int = Field(default=30, ge=1, description="Timeout for LLM requests in seconds.")
    max_retries: int = Field(default=2, ge=0, description="Number of retry attempts on failure.")


# ----------------------------
# 2. Response Cache
# ----------------------------
class ResponseCache:
    """
    A simple LRU-style cache for storing question-response pairs.
    This improves response time for frequently asked questions.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the cache with a maximum size.
        
        Args:
            max_size (int): Maximum number of cached responses. 0 disables caching.
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.enabled = max_size > 0
        
        if self.enabled:
            log.info(f"Response cache initialized with max size: {max_size}")
        else:
            log.info("Response cache disabled")
    
    def _hash_text(self, text: str) -> str:
        """Create a hash of the input text for cache key."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Retrieve a cached response for the given query.
        
        Args:
            query (str): The user's question.
            
        Returns:
            Optional[str]: Cached response if found, None otherwise.
        """
        if not self.enabled or not query:
            return None
            
        cache_key = self._hash_text(query)
        
        if cache_key in self.cache:
            self.hits += 1
            # Move to end to mark as recently used
            self.cache.move_to_end(cache_key)
            response, timestamp = self.cache[cache_key]
            log.info(f"Cache HIT for query (cached {time.time() - timestamp:.1f}s ago)")
            return response
        
        self.misses += 1
        return None
    
    def put(self, query: str, response: str):
        """
        Store a query-response pair in the cache.
        
        Args:
            query (str): The user's question.
            response (str): The LLM's response.
        """
        if not self.enabled or not query or not response:
            return
            
        cache_key = self._hash_text(query)
        
        # Remove oldest item if cache is full
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            self.cache.popitem(last=False)
        
        self.cache[cache_key] = (response, time.time())
    
    def clear(self):
        """Clear all cached responses."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        log.info("Response cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len(self.cache),
            "hit_rate": round(hit_rate, 2)
        }


# ----------------------------
# 3. Prompt Manager
# ----------------------------
class PromptManager:
    """
    Manages prompt templates and system instructions.
    Separates prompt logic from LLM processing for better maintainability.
    """
    
    def __init__(self, assistant_name: str = "Plu"):
        """
        Initialize the prompt manager.
        
        Args:
            assistant_name (str): Name of the voice assistant.
        """
        self.assistant_name = assistant_name
        self.system_prompt = self._create_system_prompt()
        self.prompt_template = self._create_prompt_template()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt that defines the assistant's behavior."""
        return (
            f"Your name is {self.assistant_name}. You are a helpful, concise, and friendly voice assistant robot. "
            "You are learned and witty, and you love to help people. "
            "You only answer questions in English. "
            "Respond to the user's query directly and clearly. Do not use markdown or any special formatting in your response. "
            "All your responses should be child appropriate, no adult content, no violent and non racist. "
            "For questions you cannot answer, respond with 'I don't know'. "
            "You must answer in the same language as the question. "
            "You can ask for clarifications if needed. "
            "Keep your responses concise and conversational, suitable for voice interaction."
        )
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for the LLM chain."""
        return ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{user_input}"),
        ])
    
    def get_template(self) -> ChatPromptTemplate:
        """Get the prompt template."""
        return self.prompt_template
    
    def update_system_prompt(self, new_prompt: str):
        """
        Update the system prompt and recreate the template.
        
        Args:
            new_prompt (str): New system prompt text.
        """
        self.system_prompt = new_prompt
        self.prompt_template = self._create_prompt_template()
        log.info("System prompt updated")


# ----------------------------
# 4. Main Processor Class
# ----------------------------
class LLMProcessor:
    """
    Handles all interactions with the local LLM (Phi-3 via Ollama).

    This class is responsible for:
    - Creating a prompt from user input.
    - Invoking the LLM with caching and retry logic.
    - Parsing the output.
    - Tracking performance metrics.
    - It follows SRP by focusing solely on LLM text processing.
    """

    def __init__(self, config: LLMConfig):
        """
        Initializes the LLM processor with a validated configuration.

        Args:
            config (LLMConfig): A Pydantic model containing the LLM settings.
        """
        self.config = config
        log.info(
            f"Initializing LLM Processor with model '{self.config.model_name}' at {self.config.base_url}"
        )

        # Initialize components
        self.prompt_manager = PromptManager()
        self.cache = ResponseCache(max_size=config.cache_size)
        
        # Performance tracking
        self.total_requests = 0
        self.total_processing_time = 0.0
        self.failed_requests = 0

        # Initialize the Ollama LLM through LangChain
        try:
            llm = Ollama(
                model=self.config.model_name, 
                base_url=str(self.config.base_url),
                timeout=self.config.timeout_seconds
            )
        except Exception as e:
            log.error(
                f"Failed to connect to Ollama at {self.config.base_url}. "
                f"Please ensure Ollama is running and the model '{self.config.model_name}' is pulled. Error: {e}"
            )
            raise

        # Define the output parser to get a clean string
        output_parser = StrOutputParser()

        # Chain the components together using LangChain Expression Language (LCEL)
        self.chain = self.prompt_manager.get_template() | llm | output_parser
        log.info("LLM interaction chain created successfully.")

    def generate_response(self, user_text: str, use_cache: bool = True) -> str:
        """
        Generates a response from the LLM based on the user's text.
        Uses caching and retry logic for improved performance and reliability.

        Args:
            user_text (str): The transcribed text from the user.
            use_cache (bool): Whether to use cached responses. Default is True.

        Returns:
            str: The LLM's generated response.
        """
        if not user_text:
            log.warning("Received empty text for processing. Returning empty response.")
            return ""

        # Normalize input
        user_text = user_text.strip()
        
        # Check cache first
        if use_cache:
            cached_response = self.cache.get(user_text)
            if cached_response:
                return cached_response

        log.info(f"Generating response for user input: {user_text}")
        start_time = time.time()

        # Try to get response with retry logic
        response = self._invoke_with_retry(user_text)
        
        # Track metrics
        processing_time = time.time() - start_time
        self.total_requests += 1
        self.total_processing_time += processing_time
        
        log.info(f"LLM response time: {processing_time:.2f} seconds")
        log.info(f"LLM Output: '{response}'")
        
        # Cache the response
        if use_cache and response:
            self.cache.put(user_text, response)
        
        return response

    def _invoke_with_retry(self, user_text: str) -> str:
        """
        Invoke the LLM chain with retry logic.
        
        Args:
            user_text (str): The user's input text.
            
        Returns:
            str: The LLM's response or error message.
        """
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.chain.invoke({"user_input": user_text})
                return response
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    log.warning(f"LLM invocation failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}")
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    log.error(f"Error during LLM invocation after {self.config.max_retries + 1} attempts: {e}")
        
        self.failed_requests += 1
        return "I'm sorry, I encountered an error while processing your request."

    def get_performance_stats(self) -> Dict[str, any]:
        """
        Get performance statistics for the LLM processor.
        
        Returns:
            Dict: Performance metrics including cache stats and processing times.
        """
        avg_time = (self.total_processing_time / self.total_requests) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round((1 - self.failed_requests / max(self.total_requests, 1)) * 100, 2),
            "avg_response_time": round(avg_time, 2),
            "total_processing_time": round(self.total_processing_time, 2),
            "cache_stats": self.cache.get_stats()
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.total_requests = 0
        self.total_processing_time = 0.0
        self.failed_requests = 0
        self.cache.hits = 0
        self.cache.misses = 0
        log.info("Performance statistics reset")

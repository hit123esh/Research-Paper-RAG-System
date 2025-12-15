"""
LLM client module for interacting with Ollama.
"""
import httpx
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (default: from env or http://localhost:11434)
            model: Model name (default: from env or "mistral")
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Get model name: use parameter, then env var, then safe default
        env_model = os.getenv("OLLAMA_MODEL", "").strip()
        if model:
            self.model = model
        elif env_model:
            self.model = env_model
        else:
            # Safe default: Ollama typically uses "mistral:latest" (not "mistral:7b")
            self.model = "mistral:latest"
        
        self.api_url = f"{self.base_url}/api/generate"
        
        # Validate model exists on startup
        self._validate_model()
    
    def _validate_model(self) -> None:
        """
        Validate that the configured model exists in Ollama.
        Raises ValueError with helpful message if model not found.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                # Extract model names from response
                available_models = []
                if "models" in data:
                    for model_info in data["models"]:
                        model_name = model_info.get("name", "")
                        if model_name:
                            available_models.append(model_name)
                
                # Check if our model exists (exact match or prefix match)
                model_found = False
                for available in available_models:
                    # Check exact match or if configured model is a prefix (e.g., "mistral" matches "mistral:latest")
                    if available == self.model or available.startswith(self.model + ":"):
                        model_found = True
                        # Use the exact name from Ollama if it's different
                        if available != self.model:
                            print(f"[Ollama] Using model '{available}' (configured as '{self.model}')")
                            self.model = available
                        break
                
                if not model_found:
                    available_str = ", ".join(available_models) if available_models else "none"
                    raise ValueError(
                        f"Configured Ollama model '{self.model}' not found. "
                        f"Available models: {available_str}. "
                        f"Run 'ollama list' to see all models and update OLLAMA_MODEL environment variable."
                    )
                
                print(f"[Ollama] Model '{self.model}' validated successfully")
                
        except httpx.RequestError as e:
            print(f"[WARNING] Could not validate Ollama model (Ollama may not be running): {e}")
            # Don't raise - allow startup to continue, but model validation will fail at runtime
        except httpx.HTTPStatusError as e:
            print(f"[WARNING] Could not validate Ollama model (HTTP {e.response.status_code}): {e.response.text}")
            # Don't raise - allow startup to continue
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            print(f"[WARNING] Unexpected error during model validation: {e}")
            # Don't raise - allow startup to continue
    
    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: User prompt/question
            context: Retrieved context from RAG
            system_prompt: System instructions
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        # Build full prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n"
        else:
            full_prompt = ""
        
        if context:
            full_prompt += f"Context from research paper(s):\n{context}\n\n"
        
        full_prompt += f"Question: {prompt}\n\nAnswer (based ONLY on the context provided):"
        
        # Prepare request
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
        except httpx.HTTPStatusError as e:
            # Handle 404 specifically for model not found
            if e.response.status_code == 404:
                error_text = e.response.text
                if "not found" in error_text.lower() or "model" in error_text.lower():
                    raise Exception(
                        f"Configured Ollama model '{self.model}' not found. "
                        f"Run 'ollama list' to see available models and update OLLAMA_MODEL environment variable."
                    )
            raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
    
    def generate_comparison(
        self,
        question: str,
        paper1_context: str,
        paper2_context: str,
        paper1_name: str,
        paper2_name: str,
        aspects: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comparison between two papers.
        
        Args:
            question: Comparison question or aspect
            paper1_context: Retrieved context from paper 1
            paper2_context: Retrieved context from paper 2
            paper1_name: Name of paper 1
            paper2_name: Name of paper 2
            aspects: List of aspects to compare
            
        Returns:
            Dictionary with comparison results
        """
        system_prompt = """You are an expert academic researcher. Your task is to compare two research papers based ONLY on the provided context. 
Do not use any external knowledge. If information is not present in the context, state that clearly.
Maintain an academic and objective tone."""
        
        context = f"""Paper 1: {paper1_name}
{paper1_context}

Paper 2: {paper2_name}
{paper2_context}"""
        
        prompt = f"""Compare the following aspects between the two papers: {', '.join(aspects)}.
For each aspect, provide:
1. What Paper 1 states (only if present in context)
2. What Paper 2 states (only if present in context)
3. Key differences or similarities (only if both papers mention the aspect)

Format your response as a structured comparison. If an aspect is not mentioned in either paper, state: "Not mentioned in the provided context."
"""
        
        response_text = self.generate(
            prompt=prompt,
            context=context,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response into structured format
        comparison = self._parse_comparison_response(response_text, aspects)
        
        return comparison
    
    def _parse_comparison_response(
        self,
        response_text: str,
        aspects: List[str]
    ) -> Dict[str, Any]:
        """
        Parse LLM comparison response into structured format.
        
        Args:
            response_text: Raw LLM response
            aspects: List of aspects
            
        Returns:
            Structured comparison dictionary
        """
        comparison = {}
        
        # Simple parsing - look for aspect mentions
        response_lower = response_text.lower()
        
        for aspect in aspects:
            aspect_lower = aspect.lower()
            # Try to extract relevant section
            comparison[aspect] = {
                "paper1": "Not mentioned in the provided context.",
                "paper2": "Not mentioned in the provided context.",
                "differences": "Not mentioned in the provided context.",
                "raw_text": response_text  # Include full response for reference
            }
        
        # For now, return the full response as raw_text for each aspect
        # In production, you might want more sophisticated parsing
        for aspect in aspects:
            comparison[aspect]["raw_text"] = response_text
        
        return comparison
    
    def check_health(self) -> bool:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


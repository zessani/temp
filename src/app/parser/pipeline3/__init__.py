"""
Pipeline 3: Hybrid Local + Cloud Resume Parser

Combines local Llama models (M1 optimized) with OpenAI models for maximum 
accuracy while minimizing cost. Routes based on document complexity.

Components:
- router.py: Determines local vs cloud processing
- local.py: Ollama + Llama 3.2 processing
- cloud.py: OpenAI processing for complex cases
- pipeline3_main.py: Main pipeline orchestrator
"""

from .pipeline3_main import Pipeline3Parser

__all__ = ['Pipeline3Parser']
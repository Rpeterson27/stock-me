"""Gemini model wrapper for generating content."""

import os
import logging
import asyncio
import google.generativeai as genai
import json
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GeminiModel:
    """Wrapper for Google's Gemini Pro model."""
    
    def __init__(self):
        """Initialize Gemini model with API key."""
        logger.debug("Initializing GeminiModel")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        logger.debug("Configuring Gemini with API key")
        genai.configure(api_key=api_key)
        logger.debug("Creating Gemini Pro model")
        self.model = genai.GenerativeModel('gemini-pro')
        logger.debug("GeminiModel initialization complete")
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini Pro model.
        
        Args:
            prompt: Input prompt for content generation
            
        Returns:
            Generated text content as valid JSON
            
        Raises:
            Exception: If content generation fails
        """
        try:
            logger.debug("Starting content generation")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Add JSON formatting instruction to prompt
            json_prompt = f"{prompt}\n\nIMPORTANT: Your response MUST be valid JSON. Do not include any text outside of the JSON object."
            
            # Run generate_content in a thread pool since it's blocking
            logger.debug("Getting event loop")
            loop = asyncio.get_running_loop()
            
            logger.debug("Running generate_content in thread pool")
            response = await loop.run_in_executor(None, self.model.generate_content, json_prompt)
            
            text = response.text.strip()
            logger.debug(f"Generated text length: {len(text)} characters")
            
            # Validate JSON
            try:
                json.loads(text)
                return text
            except json.JSONDecodeError:
                logger.error("Gemini response was not valid JSON")
                logger.debug(f"Invalid response: {text}")
                raise ValueError("Failed to generate valid JSON response")
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}", exc_info=True)
            raise

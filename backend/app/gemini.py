"""Gemini model wrapper for generating content."""

import os
import logging
import asyncio
import google.generativeai as genai
import json
from typing import Optional
import traceback
import re

class GeminiModel:
    """Wrapper for Google's Gemini Pro model."""
    
    def __init__(self):
        """Initialize the Gemini model with API key."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.debug("Initializing GeminiModel")
        
        # Configure API
        self.logger.debug("Configuring Gemini with API key")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.logger.error("GOOGLE_API_KEY environment variable not set")
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        self.logger.debug("Configuring Gemini with API key")
        genai.configure(api_key=api_key)
        
        # Create model
        self.logger.debug("Creating Gemini Pro model")
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger.debug("GeminiModel initialization complete")
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini AI."""
        try:
            self.logger.debug("Starting content generation")
            self.logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Add JSON formatting instructions
            prompt += """

            Format your response as a valid JSON object with exactly these fields:
            {
                "sentiment_summary": "Brief 1-2 sentence summary of overall market sentiment",
                "key_insights": ["List of 3-5 key insights as bullet points"],
                "full_report": "Detailed analysis in markdown format"
            }
            
            IMPORTANT: 
            1. Response MUST be valid JSON
            2. Use exactly these field names
            3. Do not add any other fields
            4. Do not include any text outside the JSON object
            5. Escape any special characters in strings
            6. Use only ASCII characters in the JSON
            7. Do not use any control characters or special formatting
            """
            
            self.logger.debug("Getting event loop")
            loop = asyncio.get_event_loop()
            
            self.logger.debug("Running generate_content in thread pool")
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            text = response.text
            self.logger.debug(f"Generated text length: {len(text)} characters")
            
            # Clean and validate the response
            def clean_json_text(text: str) -> str:
                # Remove any markdown code block markers
                text = re.sub(r'```json\s*|\s*```', '', text)
                
                # Extract the JSON object
                match = re.search(r'({[\s\S]*})', text)
                if not match:
                    raise ValueError("No JSON object found in response")
                text = match.group(1)
                
                # Remove all control characters except newlines
                text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
                
                # Ensure property names are properly quoted
                text = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', text)
                
                # Clean up any remaining formatting issues
                text = text.replace('\n', ' ').replace('\r', '')
                text = re.sub(r'\s+', ' ', text)
                
                return text
            
            # Try to parse the JSON
            try:
                text = clean_json_text(text)
                self.logger.debug(f"Cleaned JSON text: {text}")
                json_data = json.loads(text)
                return json.dumps(json_data, ensure_ascii=True)  # Re-serialize to ensure clean JSON
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON: {str(e)}")
                self.logger.debug(f"Problematic text: {text}")
                raise
            
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            self.logger.debug(traceback.format_exc())
            raise

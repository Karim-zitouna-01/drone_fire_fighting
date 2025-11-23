# AI/llm_client.py

from google import genai
import os
from dotenv import load_dotenv

 

class LLMClient:
    """
    Static wrapper for calling Gemini models.
    """
    load_dotenv()

    api_key = os.getenv("GENAI_API_KEY")
    client = genai.Client(api_key=api_key)

    @staticmethod
    def call_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
        """
        Call a Gemini model with text only.

        Args:
            prompt (str): Your instruction.
            model_name (str): Gemini model name.

        Returns:
            str: Model response text.
        """

        response = LLMClient.client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        return response.text

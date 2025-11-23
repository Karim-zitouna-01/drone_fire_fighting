# AI/llm_client.py

from google import genai


class LLMClient:
    """
    Static wrapper for calling Gemini models.
    """

    # Initialize once (later you can load API key from CONFIG)
    client = genai.Client(api_key="YOUR_API_KEY_HERE")

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

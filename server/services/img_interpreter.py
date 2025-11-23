# services/img_interpreter.py

from AI.VLM_client import VLMClient
import json


class ImgInterpreter:
    """
    Interprets an image using a Vision-Language Model (Qwen2-VL locally or Gemini API remotely).
    """

    @staticmethod
    def interpret_image(image_path: str, use_gemini: bool = True) -> dict:
        """
        Calls a VLM to describe the scene in the image.

        Args:
            image_path (str): Path to the image file.
            use_gemini (bool): If True, use Gemini API; else use local Qwen2-VL.

        Returns:
            dict: {
                'raw_description': str,
                'fire_detected': bool,
                'smoke_detected': bool
            }
        """
        prompt = """You are an analysis system helping in fire fighting.
Describe what is in the image briefly and mention risks if any.
Then answer the following in JSON only:
{
  "raw_description": "text description",
  "fire_detected": true/false,
  "smoke_detected": true/false
}
"""

        try:
            if use_gemini:
                raw = VLMClient.call_gemini(image_path, prompt)
            else:
                raw = VLMClient.call_qwen2(image_path, prompt)
        except Exception as e:
            raw = f"Error calling VLM: {e}"
            print(raw)

        # Try to extract JSON from the response
        extracted = {}
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            extracted = json.loads(raw[start:end])
        except Exception:
            # Fallback default values
            extracted = {
                "raw_description": "Parsing failed.",
                "fire_detected": False,
                "smoke_detected": False
            }

        return extracted

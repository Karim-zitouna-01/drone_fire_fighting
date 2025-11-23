# services/img_interpreter.py

from AI.VLM_client import VLMClient


class ImgInterpreter:
    """
    Interprets an image using a Vision-Language Model (Qwen2-VL for now).
    """

    @staticmethod
    def interpret_image(image_path: str) -> dict:
        """
        Calls VLM to describe the scene in the image.

        Returns:
            dict: {
                'raw_description': str,
                
                'fire_detected': bool,
                'smoke_detected': bool
            }
        """

        prompt = """You are an analysis system.
Describe clearly what you see.
Then answer the following in JSON only:
{
  "raw_description": "text description",
  "fire_detected": true/false,
  "smoke_detected": true/false
}
"""
        try:
            raw = VLMClient.call_qwen2(image_path, prompt)
        except Exception as e:
            raw = f"Error calling VLM: {e}"
            print(raw)

       
        
        import json
        extracted = {}

        try:
            # Find the first JSON-like structure
            start = raw.find("{")
            end = raw.rfind("}") + 1
            extracted = json.loads(raw[start:end])
        except Exception:
            # fallback default
            extracted = {
                "raw_description": "Parsing failed.",
                "fire_detected": False,
                "smoke_detected": False
            }

        return {
            
            **extracted
        }


# AI/VLM_client.py

from PIL import Image
import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

# For Gemini API
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()


class VLMClient:
    """
    Wrapper for Qwen2-VL (local) and Gemini (cloud).
    """

    @staticmethod
    def call_qwen2(image_path: str, prompt: str) -> str:
        """
        Lazy-loads Qwen2-VL and runs inference on a single image.
        """
        try:
            # Load processor & model inside method
            processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                "Qwen/Qwen2-VL-2B-Instruct",
                torch_dtype="auto",
                device_map="auto"
            )

            img = Image.open(image_path).convert("RGB")

            inputs = processor(
                text=prompt,
                images=img,
                return_tensors="pt"
            ).to(model.device)

            output = model.generate(**inputs, max_new_tokens=200)
            result = processor.decode(output[0], skip_special_tokens=True)

            # Free GPU memory
            del model, inputs
            torch.cuda.empty_cache()

            return result

        except Exception as e:
            return f"Error calling VLM: {e}"

    @staticmethod
    def call_gemini(image_path: str, prompt: str, model_name: str = "gemini-2.5-flash") -> str:
        """
        Call Gemini multimodal API with an image and a text prompt.
        """
        try:
            api_key = os.getenv("GENAI_API_KEY")
            if not api_key:
                return "GENAI_API_KEY not set in environment."

            client = genai.Client(api_key=api_key)

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    prompt
                ]
            )

            return response.text

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error calling Gemini API: {e}"
# Example usage:

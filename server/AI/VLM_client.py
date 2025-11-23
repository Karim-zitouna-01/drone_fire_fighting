# AI/VLM_client.py

from transformers import AutoProcessor, AutoModelForImageTextToText, Qwen2VLForConditionalGeneration
from PIL import Image
import torch

class VLMClient:
    """
    Static wrapper for Qwen2-VL-2B-Instruct
    """

    # Load once globally
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct", torch_dtype="auto", device_map="auto"
        )

    @staticmethod
    def call_qwen2(image_path: str, prompt: str) -> str:
        """
        Call Qwen2-VL with an image and text prompt.
        """
        try:
            img = Image.open(image_path).convert("RGB")

            inputs = VLMClient.processor(
                text=prompt,
                images=img,
                return_tensors="pt"
            ).to(VLMClient.model.device)


            

            output = VLMClient.model.generate(
                **inputs,
                max_new_tokens=200
            )

            result = VLMClient.processor.decode(output[0], skip_special_tokens=True)
            return result

        except Exception as e:
            return f"Error calling VLM: {e}"

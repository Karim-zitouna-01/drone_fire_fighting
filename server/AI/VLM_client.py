# AI/VLM_client.py

from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import torch


class VLMClient:
    """
    A simple static wrapper for calling Qwen2-VL.
    Model: Qwen/Qwen2-VL-2B-Instruct
    """

    # Load once globally (not inside the method) — much faster
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
    model = AutoModelForVision2Seq.from_pretrained(
        "Qwen/Qwen2-VL-2B-Instruct",
        torch_dtype=torch.float16,
        device_map="auto"
    )

    @staticmethod
    def call_qwen2(image_path: str, prompt: str) -> str:
        """
        Call Qwen2-VL with an image and a text prompt.

        Args:
            image_path (str): path to the input image.
            prompt (str): instruction to send to the VLM.

        Returns:
            str: the generated answer.
        """
        image = Image.open(image_path).convert("RGB")

        inputs = VLMClient.processor(
            text=prompt,
            images=image,
            return_tensors="pt"
        ).to(VLMClient.model.device)

        output = VLMClient.model.generate(
            **inputs,
            max_new_tokens=200
        )

        return VLMClient.processor.decode(output[0], skip_special_tokens=True)

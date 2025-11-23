# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from PIL import Image
import io
import os
from dotenv import load_dotenv
from google import genai

# ---------------------------------------
# GLOBAL VARIABLES (models loaded once)
# ---------------------------------------
vlm_model = None
vlm_processor = None
llm_client = None

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# ---------------------------------------
# FASTAPI APP
# ---------------------------------------
app = FastAPI(title="AI Server (LLM + VLM)")



# ---------------------------------------
# STARTUP: Load models 1 time only
# ---------------------------------------





# -------------------------------------------------
#  Endpoint 1 — IMAGE INTERPRETATION (Qwen2-VL)
# -------------------------------------------------
@app.post("/get_img_interpretation", response_class=JSONResponse)
async def get_img_interpretation(
    file: UploadFile = File(...),
    prompt: str = "Describe the image briefly."
):
    return {"status": "error", "message": "VLM model not initialized."}

# -------------------------------------------------
#  Endpoint 2 — TEXT LLM ANSWER (Gemini)
# -------------------------------------------------
@app.post("/get_llm_answer")
async def get_llm_answer(prompt: str):
    if llm_client is None:
        raise HTTPException(status_code=500, detail="Gemini client not initialized.")

    try:
        response = llm_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return {"status": "success", "answer": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/")
def health():
    return {"status": "ok", "message": "AI server is running."}

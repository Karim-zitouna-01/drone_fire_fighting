# services/danger_estimator.py

from AI.llm_client import LLMClient


class DangerEstimator:
    """
    Uses LLM to estimate the danger score (1-100).
    """

    @staticmethod
    def estimate_danger(img_info: dict, data_info: dict, people_count: int) -> dict:
        """
        Use an LLM to combine all information and compute a danger score.
        """

        prompt = f"""
You are a safety analysis AI.
You must output ONLY JSON.

Here is the situation:
Image info: {img_info}
Sensor-based interpretation: {data_info}
Number of people: {people_count}

Estimate the danger level (1-100), where:
1 = no danger
100 = extreme danger

Respond ONLY in JSON:
{{
    "danger_score": number,
    "reason": "text explanation"
}}
"""

        raw = LLMClient.call_gemini(prompt)

        import json
        result = {
            "danger_score": 0,
            "reason": "Parsing failed."
        }

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            result = json.loads(raw[start:end])
        except Exception:
            pass

        return result

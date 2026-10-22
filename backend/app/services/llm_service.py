"""
LLM Explanation Layer for Deepfake Detection.

Supports OpenAI-compatible API (primary) and Anthropic API.
Configuration is loaded from the llm_configs DB table at startup and
can be reloaded at runtime when admin saves new settings.
"""
import asyncio
import json
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def _compute_heatmap_stats(mask_prob: Optional[np.ndarray]) -> dict:
    """Derive simple spatial statistics from the mask probability map."""
    if mask_prob is None:
        return {}

    h, w = mask_prob.shape[:2]
    flat = mask_prob.flatten()

    quadrants = {
        "top-left":     mask_prob[: h // 2, : w // 2].mean(),
        "top-right":    mask_prob[: h // 2, w // 2 :].mean(),
        "bottom-left":  mask_prob[h // 2 :, : w // 2].mean(),
        "bottom-right": mask_prob[h // 2 :, w // 2 :].mean(),
        "center":       mask_prob[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4].mean(),
    }
    ranked = sorted(quadrants.items(), key=lambda x: x[1], reverse=True)

    return {
        "mean_activation": round(float(flat.mean()), 4),
        "max_activation": round(float(flat.max()), 4),
        "high_activation_ratio": round(float((flat > 0.5).mean()), 4),
        "top_anomalous_regions": [name for name, _ in ranked[:3]],
    }


def _build_prompt(
    is_fake: bool,
    fake_probability: float,
    confidence: float,
    risk_level: str,
    analysis: dict,
    heatmap_stats: dict,
) -> str:
    percent = round(fake_probability * 100, 1)
    conf_pct = round(confidence * 100, 1)

    heatmap_section = ""
    if heatmap_stats:
        regions = ", ".join(heatmap_stats.get("top_anomalous_regions", []))
        heatmap_section = f"""
Heatmap analysis:
- Mean activation score: {heatmap_stats.get('mean_activation', 'N/A')}
- Max activation score:  {heatmap_stats.get('max_activation', 'N/A')}
- High-activation pixel ratio: {heatmap_stats.get('high_activation_ratio', 'N/A')}
- Most anomalous spatial regions: {regions}
"""

    return f"""You are a forensic image analysis expert. A deepfake detection model has just analyzed an image.
Your task is to produce a concise, professional explanation of the results for a security analyst.

--- Detection Results ---
Verdict:          {"FAKE / Manipulated" if is_fake else "REAL / Authentic"}
Fake probability: {percent}%
Confidence:       {conf_pct}%
Risk level:       {risk_level}

Signal breakdown (0 = none, 1 = strong indicator):
- Face manipulation:     {analysis.get('face_manipulation', 'N/A')}
- Texture inconsistency: {analysis.get('texture_inconsistency', 'N/A')}
- Lighting artifacts:    {analysis.get('lighting_artifacts', 'N/A')}
- Compression anomalies: {analysis.get('compression_anomalies', 'N/A')}
{heatmap_section}
--- Instructions ---
Reply with a JSON object using exactly these four keys:

{{
  "anomalous_regions": "<1-2 sentences describing WHICH spatial areas are suspicious>",
  "why_fake": "<2-3 sentences explaining WHY the image shows signs of manipulation>",
  "risk_level_reason": "<1-2 sentences explaining the rationale for the '{risk_level}' risk classification>",
  "overall_explanation": "<3-4 sentences combining all findings into a coherent analyst-facing summary>"
}}

Return ONLY valid JSON, no extra text."""


def _mask_key(key: str) -> str:
    """Return a masked version of an API key for display."""
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


class LLMExplanationService:
    """
    Generates natural-language explanations for detection results.

    Config priority:
      1. DB config loaded via reload_config() (set on startup + admin save)
      2. Falls back to disabled state if no config loaded
    """

    def __init__(self):
        self._client = None
        self._config = {
            "provider": "openai",
            "api_base_url": "https://api.openai.com/v1",
            "api_key": "",
            "model": "gpt-4o-mini",
            "enabled": False,
            "max_tokens": 512,
            "temperature": 0.3,
        }

    def reload_config(self, db_config) -> None:
        """Load configuration from a LLMConfig DB object."""
        self._config = {
            "provider": db_config.provider or "openai",
            "api_base_url": db_config.api_base_url or "https://api.openai.com/v1",
            "api_key": db_config.api_key or "",
            "model": db_config.model or "gpt-4o-mini",
            "enabled": bool(db_config.enabled),
            "max_tokens": db_config.max_tokens or 512,
            "temperature": db_config.temperature if db_config.temperature is not None else 0.3,
        }
        self._client = None  # reset so it gets recreated with new settings
        logger.info(
            "LLM config reloaded: provider=%s model=%s enabled=%s",
            self._config["provider"],
            self._config["model"],
            self._config["enabled"],
        )

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = self._config.get("api_key", "")
        if not api_key:
            return None

        provider = self._config.get("provider", "openai")
        try:
            if provider == "anthropic":
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            else:
                # OpenAI or any OpenAI-compatible endpoint
                from openai import OpenAI
                base_url = self._config.get("api_base_url") or "https://api.openai.com/v1"
                self._client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError as e:
            logger.error("Missing SDK: %s", e)
            return None

        return self._client

    def _call_llm(self, prompt: str) -> str:
        """Send prompt to the configured LLM and return raw text."""
        client = self._get_client()
        if client is None:
            raise RuntimeError("LLM client not available")

        provider = self._config.get("provider", "openai")
        model = self._config["model"]
        max_tokens = self._config["max_tokens"]
        temperature = self._config["temperature"]

        if provider == "anthropic":
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
        else:
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()

    async def generate_explanation(
        self,
        is_fake: bool,
        fake_probability: float,
        confidence: float,
        risk_level: str,
        analysis: dict,
        mask_prob: Optional[np.ndarray] = None,
    ) -> dict:
        """Generate an LLM explanation for the detection result."""
        if not self._config.get("enabled"):
            return {"llm_error": "LLM explanation disabled"}

        if not self._config.get("api_key"):
            return {"llm_error": "API key not configured"}

        heatmap_stats = _compute_heatmap_stats(mask_prob)
        prompt = _build_prompt(
            is_fake, fake_probability, confidence, risk_level, analysis, heatmap_stats
        )

        try:
            raw = await asyncio.to_thread(self._call_llm, prompt)

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)
            result["llm_model"] = self._config["model"]
            return result

        except json.JSONDecodeError as e:
            logger.warning("LLM returned non-JSON: %s", e)
            return {"llm_error": f"JSON parse error: {e}"}
        except Exception as e:
            logger.error("LLM explanation failed: %s", e)
            return {"llm_error": str(e)}

    async def test_connection(self) -> dict:
        """Send a minimal request to verify the current configuration works."""
        if not self._config.get("api_key"):
            return {"success": False, "message": "API key not configured", "response_preview": None}

        try:
            raw = await asyncio.to_thread(
                self._call_llm, 'Reply with the single word "OK".'
            )
            return {"success": True, "message": "Connection successful", "response_preview": raw[:100]}
        except Exception as e:
            return {"success": False, "message": str(e), "response_preview": None}

    @staticmethod
    def mask_key(key: str) -> str:
        return _mask_key(key)


# Singleton
llm_service = LLMExplanationService()

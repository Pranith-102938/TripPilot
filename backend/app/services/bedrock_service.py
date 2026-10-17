"""Modular Amazon Bedrock service foundation for TripPilot Phase 5.1.

Utilizes boto3 Bedrock Runtime and standard AWS credential provider chain.
Supports configurable region and model ID with safe fallback handling when
AWS credentials or configurations are absent. Never logs credentials or prompts.
"""
import os
import re
import json
import time
import logging
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

import boto3
import botocore.session
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    ConnectTimeoutError,
    ReadTimeoutError,
    EndpointConnectionError,
)

from app.models import (
    BedrockItineraryEnrichment,
    DailyEnrichment,
    TripPlanResponse,
)

logger = logging.getLogger("trippilot.bedrock")

# Safe default model: Claude 3.5 Sonnet v2 on Amazon Bedrock
DEFAULT_BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
DEFAULT_AWS_REGION = "us-east-1"


class BedrockConfig(BaseModel):
    """Configuration options for Amazon Bedrock Runtime."""
    model_config = ConfigDict(populate_by_name=True)

    region_name: str = Field(default_factory=lambda: os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or DEFAULT_AWS_REGION)
    model_id: str = Field(default_factory=lambda: os.getenv("BEDROCK_MODEL_ID") or DEFAULT_BEDROCK_MODEL_ID)
    connect_timeout: float = Field(default=5.0)
    read_timeout: float = Field(default=15.0)
    max_retries: int = Field(default=2)


class BedrockStatusResponse(BaseModel):
    """Status information for Amazon Bedrock Runtime availability."""
    status: str = Field(..., description="'available' or 'provider_unavailable'")
    region: str
    model_id: str
    has_credentials: bool
    credential_source: Optional[str] = None
    error: Optional[str] = None


class BedrockInvocationResult(BaseModel):
    """Structured response returned by Bedrock model operations."""
    status: str = Field(..., description="'success', 'provider_unavailable', or 'error'")
    model_id: str
    region: str
    text: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class BedrockService:
    """Service wrapping boto3 Amazon Bedrock Runtime with standard credential resolution."""

    def __init__(
        self,
        config: Optional[BedrockConfig] = None,
        client: Optional[Any] = None,
    ):
        self.config = config or BedrockConfig()
        self._custom_client = client

    def get_status(self) -> BedrockStatusResponse:
        """Inspects AWS credential availability and configuration without making remote network calls."""
        if self._custom_client is not None:
            return BedrockStatusResponse(
                status="available",
                region=self.config.region_name,
                model_id=self.config.model_id,
                has_credentials=True,
                credential_source="custom_client",
            )

        session = botocore.session.get_session()
        credentials = session.get_credentials()

        if credentials is None:
            return BedrockStatusResponse(
                status="provider_unavailable",
                region=self.config.region_name,
                model_id=self.config.model_id,
                has_credentials=False,
                error=(
                    "AWS credentials not detected. Configure credentials via environment variables "
                    "(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY), AWS profile, or IAM role."
                ),
            )

        return BedrockStatusResponse(
            status="available",
            region=self.config.region_name,
            model_id=self.config.model_id,
            has_credentials=True,
            credential_source=getattr(credentials, "method", "standard_chain"),
        )

    def _get_client(self) -> Tuple[Optional[Any], Optional[str]]:
        """Returns initialized Bedrock Runtime client or error message without raising unhandled exceptions."""
        if self._custom_client is not None:
            return self._custom_client, None

        status = self.get_status()
        if not status.has_credentials:
            return None, status.error

        try:
            boto_config = Config(
                connect_timeout=self.config.connect_timeout,
                read_timeout=self.config.read_timeout,
                retries={"max_attempts": self.config.max_retries},
            )
            client = boto3.client(
                "bedrock-runtime",
                region_name=self.config.region_name,
                config=boto_config,
            )
            return client, None
        except Exception as exc:
            logger.warning("Failed to initialize Bedrock Runtime client: %s", exc.__class__.__name__)
            return None, f"Failed to initialize Bedrock Runtime client: {str(exc)}"

    def converse(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> BedrockInvocationResult:
        """Invokes Bedrock model using the Converse API with safe error handling and without prompt logging."""
        client, error_msg = self._get_client()
        if client is None:
            return BedrockInvocationResult(
                status="provider_unavailable",
                model_id=self.config.model_id,
                region=self.config.region_name,
                error=error_msg,
            )

        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]

        system = [{"text": system_prompt}] if system_prompt else None
        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
        }

        started_at = time.perf_counter()

        try:
            kwargs: Dict[str, Any] = {
                "modelId": self.config.model_id,
                "messages": messages,
                "inferenceConfig": inference_config,
            }
            if system:
                kwargs["system"] = system

            response = client.converse(**kwargs)
            elapsed_ms = (time.perf_counter() - started_at) * 1000

            # Extract generated response text
            output_msg = response.get("output", {}).get("message", {})
            content_blocks = output_msg.get("content", [])
            extracted_text = "".join(b.get("text", "") for b in content_blocks if "text" in b)

            # Extract usage metrics safely
            raw_usage = response.get("usage", {})
            usage = {
                "input_tokens": raw_usage.get("inputTokens", 0),
                "output_tokens": raw_usage.get("outputTokens", 0),
                "total_tokens": raw_usage.get("totalTokens", 0),
            }

            return BedrockInvocationResult(
                status="success",
                model_id=self.config.model_id,
                region=self.config.region_name,
                text=extracted_text,
                usage=usage,
                latency_ms=round(elapsed_ms, 2),
            )

        except (NoCredentialsError, ClientError) as exc:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            error_code = exc.response.get("Error", {}).get("Code") if isinstance(exc, ClientError) else "NoCredentials"
            clean_error = f"AWS Bedrock ClientError [{error_code}]: {exc}" if isinstance(exc, ClientError) else str(exc)
            logger.warning("Bedrock invocation failed for model %s: %s", self.config.model_id, error_code)
            return BedrockInvocationResult(
                status="error",
                model_id=self.config.model_id,
                region=self.config.region_name,
                latency_ms=round(elapsed_ms, 2),
                error=clean_error,
            )
        except (ConnectTimeoutError, ReadTimeoutError) as exc:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.warning("Bedrock timeout after %.1fms for model %s", elapsed_ms, self.config.model_id)
            return BedrockInvocationResult(
                status="error",
                model_id=self.config.model_id,
                region=self.config.region_name,
                latency_ms=round(elapsed_ms, 2),
                error=f"Bedrock request timed out: {exc.__class__.__name__}",
            )
        except (BotoCoreError, EndpointConnectionError) as exc:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.warning("Bedrock connection error: %s", exc.__class__.__name__)
            return BedrockInvocationResult(
                status="error",
                model_id=self.config.model_id,
                region=self.config.region_name,
                latency_ms=round(elapsed_ms, 2),
                error=f"Bedrock connection failure: {exc.__class__.__name__}",
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.error("Unexpected error during Bedrock call: %s", exc.__class__.__name__)
            return BedrockInvocationResult(
                status="error",
                model_id=self.config.model_id,
                region=self.config.region_name,
                latency_ms=round(elapsed_ms, 2),
                error=f"Unexpected Bedrock error: {str(exc)}",
            )

    def generate_travel_narrative(
        self,
        destination: str,
        duration_days: int,
        travel_style: str,
        highlights: Optional[List[str]] = None,
    ) -> BedrockInvocationResult:
        """High-level generative synthesis method for crafting detailed travel narratives."""
        status = self.get_status()
        if not status.has_credentials:
            return BedrockInvocationResult(
                status="provider_unavailable",
                model_id=self.config.model_id,
                region=self.config.region_name,
                error=status.error,
            )

        hl_str = ", ".join(highlights) if highlights else "local regional attractions"
        prompt = (
            f"Craft an evocative, practical travel summary for a {duration_days}-day trip to {destination} "
            f"under {travel_style.title()} style, featuring highlights such as {hl_str}. "
            "Include cultural etiquette tips and distinctive regional cuisine experiences."
        )
        system_prompt = (
            "You are a sophisticated, culturally knowledgeable travel editor for TripPilot. "
            "Provide elegant, accurate, and concise prose without generic fluff."
        )

        return self.converse(prompt=prompt, system_prompt=system_prompt, max_tokens=800)

    def enrich_itinerary(
        self,
        itinerary: TripPlanResponse,
    ) -> BedrockItineraryEnrichment:
        """Enriches a deterministic itinerary using Amazon Bedrock.

        Extracts personalized narrative overview, cultural guidance, regional food recommendations,
        and daily practical tips based on the validated plan. Never alters any deterministic fields,
        dates, activities, or budget figures.
        """
        status = self.get_status()
        if not status.has_credentials:
            return BedrockItineraryEnrichment(
                status="provider_unavailable",
                model_id=self.config.model_id,
                error=status.error or "AWS credentials not detected. Configure AWS credentials to enable Amazon Bedrock itinerary enrichment.",
            )

        # Build structured schedule summary from deterministic plan
        dest_name = getattr(itinerary.destination, "name", "the destination")
        dest_state = getattr(itinerary.destination, "state", "")
        days_summary = []
        for day in itinerary.active_days:
            activities = []
            if day.morning and day.morning.title:
                activities.append(f"Morning: {day.morning.title}")
            if day.afternoon and day.afternoon.title:
                activities.append(f"Afternoon: {day.afternoon.title}")
            if day.evening and day.evening.title:
                activities.append(f"Evening: {day.evening.title}")
            days_summary.append(f"Day {day.day_number} ({day.theme}): {'; '.join(activities)}")

        schedule_text = "\n".join(days_summary)

        prompt = (
            f"You are enriching an existing verified travel itinerary for {dest_name}, {dest_state} ({itinerary.num_days} days, {itinerary.travel_style} style).\n\n"
            f"Here is the confirmed schedule:\n{schedule_text}\n\n"
            "Generate an enrichment package in valid JSON format with the following keys:\n"
            "- \"narrative\": A concise 2-3 sentence evocative overview synthesizing this trip.\n"
            "- \"cultural_guidance\": Key cultural etiquette, local customs, and respect considerations for this region.\n"
            "- \"local_food_guide\": Iconic regional dishes and dining experiences recommended for this journey.\n"
            "- \"daily_insights\": An array of objects for each day, each containing:\n"
            "    - \"day_number\": integer corresponding to the day number\n"
            "    - \"theme_note\": 1 concise sentence highlighting the day's special character\n"
            "    - \"practical_tip\": 1 specific tip (clothing, timing, gear, or navigation)\n"
            "    - \"culinary_highlight\": 1 local delicacy or meal recommendation for this day\n\n"
            "CRITICAL: Do NOT alter, calculate, or mention costs or budget figures. Return ONLY valid JSON."
        )

        system_prompt = (
            "You are a sophisticated, culturally knowledgeable travel editor for TripPilot. "
            "You provide engaging, practical enrichment for travel itineraries. "
            "Always return strictly valid JSON matching the requested schema without markdown backticks or extra commentary."
        )

        call_result = self.converse(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.6,
        )

        if call_result.status != "success":
            return BedrockItineraryEnrichment(
                status=call_result.status,
                model_id=self.config.model_id,
                latency_ms=call_result.latency_ms,
                error=call_result.error or "Bedrock model invocation failed",
            )

        # Parse JSON output robustly
        raw_text = (call_result.text or "").strip()
        parsed_data = None

        if "```" in raw_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
            if match:
                candidate = match.group(1).strip()
                try:
                    parsed_data = json.loads(candidate)
                except Exception:
                    pass

        if parsed_data is None:
            try:
                parsed_data = json.loads(raw_text)
            except Exception:
                start_idx = raw_text.find("{")
                end_idx = raw_text.rfind("}")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    try:
                        parsed_data = json.loads(raw_text[start_idx : end_idx + 1])
                    except Exception:
                        pass

        if not isinstance(parsed_data, dict):
            logger.warning("Failed to parse valid JSON from Bedrock response: %s", raw_text[:120])
            return BedrockItineraryEnrichment(
                status="error",
                model_id=self.config.model_id,
                narrative=raw_text[:400] if raw_text else None,
                latency_ms=call_result.latency_ms,
                error="Model output could not be parsed into expected structured JSON format.",
            )

        daily_insights: List[DailyEnrichment] = []
        raw_insights = parsed_data.get("daily_insights") or parsed_data.get("dailyInsights") or []
        if isinstance(raw_insights, list):
            for i, item in enumerate(raw_insights):
                if isinstance(item, dict):
                    day_num = item.get("day_number") or item.get("dayNumber") or (i + 1)
                    daily_insights.append(
                        DailyEnrichment(
                            day_number=int(day_num),
                            theme_note=item.get("theme_note") or item.get("themeNote"),
                            practical_tip=item.get("practical_tip") or item.get("practicalTip"),
                            culinary_highlight=item.get("culinary_highlight") or item.get("culinaryHighlight"),
                        )
                    )

        return BedrockItineraryEnrichment(
            status="enriched",
            model_id=self.config.model_id,
            narrative=parsed_data.get("narrative"),
            cultural_guidance=parsed_data.get("cultural_guidance") or parsed_data.get("culturalGuidance"),
            local_food_guide=parsed_data.get("local_food_guide") or parsed_data.get("localFoodGuide"),
            daily_insights=daily_insights,
            latency_ms=call_result.latency_ms,
        )


def apply_bedrock_enrichment(
    itinerary: TripPlanResponse,
    bedrock_service: Optional[BedrockService] = None,
) -> TripPlanResponse:
    """Enriches a TripPlanResponse with Bedrock AI narrative and tips.

    GUARANTEE: The deterministic itinerary is the absolute source of truth.
    All destinations, dates, activities, durations, and all budget numbers
    (dailyStay, dailyFood, accommodationCost, totalEstimatedCost, deficit, etc.)
    remain completely unchanged.
    """
    service = bedrock_service or BedrockService()
    enrichment = service.enrich_itinerary(itinerary)
    return itinerary.model_copy(update={"ai_enrichment": enrichment})

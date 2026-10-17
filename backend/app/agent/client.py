"""Client for Strands Decider 2B System One decision model."""
import os
import logging
from typing import Any, Dict, Optional
import httpx
from strands_decider.schema import (
    SystemOneRequest,
    SystemOneResponse,
    ChoiceQuestion,
    ChoiceAnswer,
    NoulQuestion,
    NoulAnswer,
    Question,
)

logger = logging.getLogger("trippilot.strands_decider")


class StrandsDeciderProviderError(Exception):
    """Raised when the Strands Decider 2B model provider is unreachable or returns an error."""
    def __init__(self, message: str, endpoint: str, details: Optional[str] = None):
        super().__init__(message)
        self.endpoint = endpoint
        self.details = details


class StrandsDeciderClient:
    """Client for Strands Decider 2B System One model (HTTP endpoint or local engine)."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.endpoint = (
            endpoint
            or os.getenv("STRANDS_DECIDER_ENDPOINT", "http://127.0.0.1:8001/v1/systemone")
        )
        self.model_name = (
            model_name
            or os.getenv("STRANDS_DECIDER_MODEL", "StrandsAgents/strands-decider-2B")
        )
        self.api_key = api_key or os.getenv("STRANDS_DECIDER_API_KEY", "")
        self.timeout = timeout
        self.device = os.getenv("STRANDS_DECIDER_DEVICE", "cpu")
        self.local_checkpoint = os.getenv("STRANDS_DECIDER_LOCAL_CHECKPOINT", "")
        self._local_engine = None

    def get_provider_status(self) -> Dict[str, Any]:
        """Checks connectivity to the Strands Decider 2B inference endpoint."""
        health_url = self.endpoint.replace("/v1/systemone", "/health")
        try:
            with httpx.Client(timeout=1.5) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                resp = client.get(health_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "available": True,
                        "endpoint": self.endpoint,
                        "model": self.model_name,
                        "device": data.get("device", self.device),
                        "checkpoint": data.get("checkpoint", self.model_name),
                        "error": None,
                    }
        except Exception as exc:
            logger.debug("Strands Decider endpoint health check failed: %s", exc)

        return {
            "available": False,
            "endpoint": self.endpoint,
            "model": self.model_name,
            "device": self.device,
            "error": (
                f"Strands Decider 2B server is unreachable at {self.endpoint}. "
                "Ensure `strands-decider serve StrandsAgents/strands-decider-2B --port 8001` is running "
                "or configure STRANDS_DECIDER_ENDPOINT in your environment."
            ),
        }

    def ask(self, state: str, questions: Dict[str, Question]) -> SystemOneResponse:
        """Sends a SystemOneRequest to Strands Decider 2B endpoint and validates the response."""
        request = SystemOneRequest(
            state=state,
            questions=questions,
            model=self.model_name,
        )

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    self.endpoint,
                    content=request.model_dump_json(),
                    headers=headers,
                )

                if resp.status_code == 200:
                    return SystemOneResponse.model_validate(resp.json())
                else:
                    raise StrandsDeciderProviderError(
                        f"Strands Decider returned HTTP {resp.status_code}: {resp.text}",
                        endpoint=self.endpoint,
                        details=resp.text,
                    )
        except httpx.RequestError as exc:
            # Check local engine fallback if local checkpoint is set
            if self.local_checkpoint:
                return self._evaluate_local(request)

            raise StrandsDeciderProviderError(
                f"Failed to connect to Strands Decider 2B inference server at {self.endpoint}: {str(exc)}",
                endpoint=self.endpoint,
                details=str(exc),
            ) from exc

    def ask_choice(
        self,
        state: str,
        instructions: str,
        criteria: Dict[str, str],
        question_id: str = "tool_choice",
    ) -> ChoiceAnswer:
        """Evaluates a multiple-choice question with calibrated confidence using Strands Decider 2B."""
        choice_q = ChoiceQuestion(
            instructions=instructions,
            criteria=criteria,
        )
        response = self.ask(state=state, questions={question_id: choice_q})
        answer = response.answers.get(question_id)
        if not isinstance(answer, ChoiceAnswer):
            raise StrandsDeciderProviderError(
                f"Expected ChoiceAnswer from Strands Decider for question '{question_id}', got {type(answer)}",
                endpoint=self.endpoint,
            )
        return answer

    def ask_noul(
        self,
        state: str,
        instructions: str,
        criteria: Optional[Dict[str, str]] = None,
        question_id: str = "yes_no_check",
    ) -> NoulAnswer:
        """Evaluates a binary yes/no question using Strands Decider 2B."""
        noul_q = NoulQuestion(
            instructions=instructions,
            criteria=criteria,
        )
        response = self.ask(state=state, questions={question_id: noul_q})
        answer = response.answers.get(question_id)
        if not isinstance(answer, NoulAnswer):
            raise StrandsDeciderProviderError(
                f"Expected NoulAnswer from Strands Decider for question '{question_id}', got {type(answer)}",
                endpoint=self.endpoint,
            )
        return answer

    def _evaluate_local(self, request: SystemOneRequest) -> SystemOneResponse:
        """Evaluates request in-process using local weights if available."""
        if self._local_engine is None:
            try:
                from strands_decider.infer import load_engine
                logger.info("Loading local Strands Decider model from %s on %s...", self.local_checkpoint, self.device)
                self._local_engine = load_engine(self.local_checkpoint, device=self.device)
            except Exception as exc:
                raise StrandsDeciderProviderError(
                    f"Failed to load local Strands Decider checkpoint '{self.local_checkpoint}': {exc}",
                    endpoint="local",
                    details=str(exc),
                ) from exc

        return self._local_engine.evaluate(request)

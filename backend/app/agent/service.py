"""Agent Service integrating Strands Agents SDK and Decider 2B for autonomous tool selection."""
import re
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.models import TripPlanRequest, TripPlanResponse
from app.services.trip_planner import create_trip_plan
from app.agent.schemas import (
    AgentPlanRequest,
    AgentPlanResponse,
    ToolSelectionTrace,
)
from app.agent.client import StrandsDeciderClient, StrandsDeciderProviderError
from app.agent.tools import (
    STRANDS_REGISTERED_TOOLS,
    DECIDER_FINISH_OPTION,
    DECIDER_FINISH_CRITERIA,
    strands_optimize_budget,
    strands_adjust_trip_duration,
    strands_adjust_travel_style,
    strands_select_interest_activities,
    strands_validate_trip_constraints,
)

logger = logging.getLogger("trippilot.strands_agent")


class StrandsAgentService:
    """Orchestrates autonomous travel planning using Strands Decider 2B and Strands @tools."""

    def __init__(self, client: Optional[StrandsDeciderClient] = None):
        self.client = client or StrandsDeciderClient()

    def plan(self, request: AgentPlanRequest) -> AgentPlanResponse:
        """Executes the agent decision loop using Strands Decider 2B for sequential tool selection."""
        # 1. Check provider availability - NEVER claim the agent ran if the provider is unavailable
        provider_status = self.client.get_provider_status()
        if not provider_status["available"]:
            return self._handle_provider_unavailable(request, provider_status)

        # 2. Resolve or generate baseline working itinerary
        working_itinerary = self._resolve_initial_itinerary(request)
        if working_itinerary is None:
            return AgentPlanResponse(
                status="error",
                model=self.client.model_name,
                execution_mode="none",
                explanation="Could not resolve or generate an initial itinerary. Please specify a destination or provide an existing itinerary.",
                provider_status=provider_status,
                error="Missing destination or itinerary",
            )

        # 3. Autonomous Tool Selection Loop via Strands Decider 2B
        tool_traces: List[ToolSelectionTrace] = []
        selected_tools: List[str] = []
        max_steps = 4

        for step in range(1, max_steps + 1):
            # Formulate current state string for Strands Decider 2B
            state = self._build_state_string(request, working_itinerary, selected_tools)

            # Build candidate tool criteria dictionary for ChoiceQuestion
            criteria = {}
            for name, meta in STRANDS_REGISTERED_TOOLS.items():
                if name not in selected_tools or name == "validate_trip_constraints":
                    criteria[name] = meta["criteria"]
            criteria[DECIDER_FINISH_OPTION] = DECIDER_FINISH_CRITERIA

            try:
                # Strands Decider 2B decides which tool to call next
                decision = self.client.ask_choice(
                    state=state,
                    instructions=(
                        "Based on the user's travel planning request and the current trip itinerary state, "
                        "which planning tool should be invoked next to fulfill their request?"
                    ),
                    criteria=criteria,
                    question_id=f"step_{step}_tool_selection",
                )
            except StrandsDeciderProviderError as exc:
                logger.error("Decider 2B call failed at step %d: %s", step, exc)
                return AgentPlanResponse(
                    status="error",
                    model=self.client.model_name,
                    execution_mode="strands_decider_2b_live",
                    explanation=f"Strands Decider 2B encountered a provider error during step {step}: {exc}",
                    selected_tools=selected_tools,
                    tool_traces=tool_traces,
                    itinerary=working_itinerary,
                    provider_status=provider_status,
                    error=str(exc),
                )

            chosen_action = decision.choice
            confidence = decision.confidence
            probabilities = decision.probabilities

            logger.info(
                "Step %d: Strands Decider 2B selected '%s' (confidence: %.2f)",
                step, chosen_action, confidence
            )

            # Check if Decider 2B concluded planning
            if chosen_action == DECIDER_FINISH_OPTION:
                break

            # Execute the chosen Strands tool
            trace, updated_itinerary = self._execute_tool(
                step=step,
                tool_name=chosen_action,
                confidence=confidence,
                probabilities=probabilities,
                user_request=request.user_request,
                request=request,
                current_itinerary=working_itinerary,
            )

            tool_traces.append(trace)
            selected_tools.append(chosen_action)
            if updated_itinerary is not None:
                working_itinerary = updated_itinerary

        # 4. Generate structured explanation and response
        explanation = self._build_agent_explanation(selected_tools, tool_traces, working_itinerary)

        return AgentPlanResponse(
            status="success",
            model=self.client.model_name,
            execution_mode="strands_decider_2b_live",
            explanation=explanation,
            selected_tools=selected_tools,
            tool_traces=tool_traces,
            itinerary=working_itinerary,
            provider_status=provider_status,
        )

    def _handle_provider_unavailable(
        self, request: AgentPlanRequest, provider_status: Dict[str, Any]
    ) -> AgentPlanResponse:
        """Transparently reports that the real Strands Decider 2B provider is offline without fake execution."""
        working_itinerary = self._resolve_initial_itinerary(request)
        return AgentPlanResponse(
            status="provider_unavailable",
            model=self.client.model_name,
            execution_mode="provider_unavailable",
            explanation=(
                f"Strands Decider 2B model server is not connected at {provider_status.get('endpoint')}. "
                "TripPilot does not simulate or fake AI reasoning. To enable genuine Strands Decider 2B "
                "autonomous tool selection, launch the model server with: "
                f"`strands-decider serve {self.client.model_name} --port 8001` "
                "or set STRANDS_DECIDER_ENDPOINT in your environment."
            ),
            selected_tools=[],
            tool_traces=[],
            itinerary=working_itinerary,
            provider_status=provider_status,
            error=provider_status.get("error"),
        )

    def _resolve_initial_itinerary(self, request: AgentPlanRequest) -> Optional[TripPlanResponse]:
        """Resolves existing itinerary or generates initial baseline plan."""
        if request.current_itinerary:
            return request.current_itinerary

        destination_id = request.destination_id or request.destination_name
        if not destination_id:
            # Attempt to extract known destination from user_request
            dest_match = self._extract_destination_from_text(request.user_request)
            if dest_match:
                destination_id = dest_match

        if destination_id:
            known_ids = [
                "hyderabad", "goa", "jaipur", "munnar", "varanasi", "ladakh",
                "udaipur", "rishikesh", "alleppey", "darjeeling", "coorg",
                "manali", "pondicherry", "agra", "andaman", "ooty", "shimla",
                "amritsar", "hampi", "mysore", "gangtok", "shillong", "jaisalmer",
                "gokarna", "khajuraho"
            ]
            is_custom = destination_id.lower() not in known_ids
            interests = request.interests or self._extract_interests(request.user_request) or ["Heritage", "Nature"]
            plan_req = TripPlanRequest(
                starting_city=request.starting_city or "New Delhi",
                destination_id="custom" if is_custom else destination_id.lower(),
                custom_destination_name=destination_id if is_custom else None,
                is_custom_destination=is_custom,
                days=request.duration or 3,
                budget=max(5000.0, float(request.budget or 20000.0)),
                interests=interests,
                travel_style=request.travel_style or "balanced",
            )
            return create_trip_plan(plan_req)

        return None


    def _build_state_string(
        self,
        request: AgentPlanRequest,
        itinerary: TripPlanResponse,
        executed_tools: List[str],
    ) -> str:
        """Builds a concise, structured state representation for Decider 2B."""
        num_days = getattr(itinerary, "num_days", getattr(itinerary, "numDays", 3))
        travel_style = getattr(itinerary, "travel_style", getattr(itinerary, "travelStyle", "balanced"))
        user_budget = getattr(itinerary, "user_budget", getattr(itinerary, "userBudget", 20000.0))
        total_cost = getattr(itinerary, "total_estimated_cost", getattr(itinerary, "totalEstimatedCost", 0))
        is_over = getattr(itinerary, "is_over_budget", getattr(itinerary, "isOverBudget", False))
        budget_opt = getattr(itinerary, "budget_optimized", getattr(itinerary, "budgetOptimized", False))

        return (
            f"User Travel Request: {request.user_request}\n"
            f"Destination: {itinerary.destination.name} ({itinerary.destination.state})\n"
            f"Duration: {num_days} days\n"
            f"Travel Style: {str(travel_style).title()}\n"
            f"User Budget: INR {user_budget:,.0f}\n"
            f"Total Estimated Cost: INR {total_cost:,.0f}\n"
            f"Deficit: INR {itinerary.deficit:,.0f} (Is Over Budget: {is_over})\n"
            f"Budget Optimized: {budget_opt}\n"
            f"Already Executed Tools in this session: {', '.join(executed_tools) if executed_tools else 'None'}"
        )

    def _execute_tool(
        self,
        step: int,
        tool_name: str,
        confidence: float,
        probabilities: Dict[str, float],
        user_request: str,
        request: AgentPlanRequest,
        current_itinerary: TripPlanResponse,
    ) -> Tuple[ToolSelectionTrace, Optional[TripPlanResponse]]:
        """Executes the specific Strands tool chosen by Decider 2B."""
        inputs: Dict[str, Any] = {}
        output_summary = ""
        updated_itinerary: Optional[TripPlanResponse] = None

        curr_days = getattr(current_itinerary, "num_days", getattr(current_itinerary, "numDays", 3))
        curr_budget = getattr(current_itinerary, "user_budget", getattr(current_itinerary, "userBudget", 20000.0))
        curr_style = str(getattr(current_itinerary, "travel_style", getattr(current_itinerary, "travelStyle", "balanced")))
        curr_is_over = getattr(current_itinerary, "is_over_budget", getattr(current_itinerary, "isOverBudget", False))
        curr_verified = getattr(current_itinerary, "is_verified", getattr(current_itinerary, "isVerified", True))

        if tool_name == "optimize_budget":
            # Extract target budget from user text if mentioned, else request.budget or current plan budget
            extracted_budget = self._extract_budget(user_request)
            target_budget = extracted_budget or request.budget or curr_budget
            inputs = {"target_budget": target_budget}
            res = strands_optimize_budget(itinerary=current_itinerary, target_budget=target_budget)
            updated_itinerary = res.revised_itinerary
            output_summary = (
                f"Optimized budget for target INR {target_budget:,.0f}. "
                f"Deficit went from INR {res.initial_deficit:,.0f} to INR {res.final_deficit:,.0f}. "
                f"Actions applied: {', '.join(res.changes_made) if res.changes_made else 'None needed'}."
            )

        elif tool_name == "adjust_trip_duration":
            extracted_days = self._extract_duration(user_request)
            if extracted_days and extracted_days != curr_days:
                target_days = extracted_days
            elif request.duration and request.duration != curr_days:
                target_days = request.duration
            else:
                # Default adjustment: shorten if overbudget, extend if explicitly mentioned
                if "extend" in user_request.lower() or "add" in user_request.lower() or "more" in user_request.lower():
                    target_days = min(30, curr_days + 1)
                else:
                    target_days = max(1, curr_days - 1)
            inputs = {"target_days": target_days}
            res = strands_adjust_trip_duration(itinerary=current_itinerary, target_days=target_days)
            updated_itinerary = res.revised_itinerary
            output_summary = f"Adjusted duration from {res.original_days} to {res.target_days} days. {res.explanation}"

        elif tool_name == "adjust_travel_style":
            extracted_style = self._extract_travel_style(user_request)
            target_style = extracted_style or request.travel_style or ("budget" if curr_is_over else "comfort")
            inputs = {"target_style": target_style}
            res = strands_adjust_travel_style(itinerary=current_itinerary, target_style=target_style)
            updated_itinerary = res.revised_itinerary
            output_summary = (
                f"Changed travel style from {res.original_style} to {res.target_style}. "
                f"Cost delta: INR {res.cost_delta:,.0f}. {res.explanation}"
            )


        elif tool_name == "select_interest_activities":
            interests = request.interests or self._extract_interests(user_request)
            inputs = {
                "destination": current_itinerary.destination.id,
                "interests": interests,
                "days": curr_days,
                "travel_style": curr_style,
                "is_custom_destination": not curr_verified,
            }
            res = strands_select_interest_activities(
                destination=current_itinerary.destination.id,
                interests=interests,
                days=curr_days,
                travel_style=curr_style,
                is_custom_destination=not curr_verified,
            )
            updated_itinerary = current_itinerary
            output_summary = (
                f"Selected and ranked activities for interests {interests}. "
                f"Matched {len(res.selected_activities)} activities across {len(res.matched_interests)} categories. "
                f"{res.rationale_summary}"
            )

        elif tool_name == "validate_trip_constraints":
            starting_city = getattr(current_itinerary, "starting_city", getattr(current_itinerary, "startingCity", "New Delhi"))
            inputs = {
                "destination": current_itinerary.destination.id,
                "days": curr_days,
                "budget": curr_budget,
                "travel_style": curr_style,
                "interests": request.interests or self._extract_interests(user_request),
                "starting_city": starting_city,
                "is_custom_destination": not curr_verified,
            }
            res = strands_validate_trip_constraints(
                destination=current_itinerary.destination.id,
                days=curr_days,
                budget=curr_budget,
                travel_style=curr_style,
                interests=request.interests or self._extract_interests(user_request),
                starting_city=starting_city,
                is_custom_destination=not curr_verified,
            )
            updated_itinerary = current_itinerary
            status_text = "Passed" if res.is_valid else f"Detected {len(res.errors)} errors, {len(res.conflicts_detected)} conflicts"
            output_summary = (
                f"Constraint validation {status_text}. Feasible budget range: INR {res.feasible_budget_min:,.0f} - {res.feasible_budget_max:,.0f}. "
                f"Recommendations: {'; '.join(res.recommendations) if res.recommendations else 'None'}."
            )
        else:
            output_summary = f"Unknown tool '{tool_name}' invoked."


        trace = ToolSelectionTrace(
            step=step,
            tool_name=tool_name,
            confidence=round(confidence, 4),
            probabilities={k: round(v, 4) for k, v in probabilities.items()},
            rationale=f"Selected '{tool_name}' with {confidence:.1%} confidence based on request analysis.",
            inputs=inputs,
            output_summary=output_summary,
            is_success=True,
        )

        return trace, updated_itinerary

    def _build_agent_explanation(
        self,
        selected_tools: List[str],
        traces: List[ToolSelectionTrace],
        final_itinerary: TripPlanResponse,
    ) -> str:
        """Synthesizes a clear, editorial summary of the agent's actions."""
        if not selected_tools:
            return "Strands Decider 2B evaluated your request and determined that no modifications were needed."

        tool_descriptions = [f"{t.tool_name} (step {t.step}, {t.confidence:.0%} confidence)" for t in traces]
        actions_str = ", ".join(tool_descriptions)

        final_days = getattr(final_itinerary, "num_days", getattr(final_itinerary, "numDays", 3))
        final_style = str(getattr(final_itinerary, "travel_style", getattr(final_itinerary, "travelStyle", "balanced")))
        final_cost = getattr(final_itinerary, "total_estimated_cost", getattr(final_itinerary, "totalEstimatedCost", 0))
        final_budget = getattr(final_itinerary, "user_budget", getattr(final_itinerary, "userBudget", 0))
        final_is_over = getattr(final_itinerary, "is_over_budget", getattr(final_itinerary, "isOverBudget", False))

        budget_status = (
            f"Trip is on budget (INR {final_cost:,.0f} of INR {final_budget:,.0f})."
            if not final_is_over
            else f"Remaining deficit is INR {final_itinerary.deficit:,.0f}."
        )

        return (
            f"Strands Decider 2B autonomously orchestrated {len(selected_tools)} planning tool(s): {actions_str}. "
            f"The revised plan covers {final_days} days in {final_itinerary.destination.name} "
            f"under {final_style.title()} style. {budget_status}"
        )


    # Regex and heuristic extractors for natural language parsing
    def _extract_destination_from_text(self, text: str) -> Optional[str]:
        known = [
            "hyderabad", "goa", "jaipur", "munnar", "varanasi", "ladakh",
            "udaipur", "rishikesh", "alleppey", "darjeeling", "coorg",
            "manali", "pondicherry", "agra", "andaman", "ooty", "shimla",
            "amritsar", "hampi", "mysore", "gangtok", "shillong", "jaisalmer",
            "gokarna", "khajuraho"
        ]
        text_lower = text.lower()
        for k in known:
            if k in text_lower:
                return k
        return None

    def _extract_duration(self, text: str) -> Optional[int]:
        m = re.search(r"(\b\d{1,2})\s*(?:day|days|d\b)", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 30:
                return val
        return None

    def _extract_budget(self, text: str) -> Optional[float]:
        m = re.search(r"(?:inr|rs\.?|₹|\$)?\s*(\d{1,3}(?:,\d{3})+|\d{4,7})\b", text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(",", "")
            val = float(raw)
            if val >= 500:
                return val
        return None

    def _extract_travel_style(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if "comfort" in text_lower or "luxury" in text_lower or "premium" in text_lower:
            return "comfort"
        if "budget" in text_lower or "cheap" in text_lower or "economy" in text_lower:
            return "budget"
        if "balanced" in text_lower or "standard" in text_lower:
            return "balanced"
        return None

    def _extract_interests(self, text: str) -> List[str]:
        interests = []
        text_lower = text.lower()
        if "nature" in text_lower or "wildlife" in text_lower or "outdoor" in text_lower:
            interests.append("Nature")
        if "beach" in text_lower or "sea" in text_lower or "coastal" in text_lower:
            interests.append("Beaches")
        if "heritage" in text_lower or "history" in text_lower or "culture" in text_lower or "temple" in text_lower:
            interests.append("Heritage")
        if "food" in text_lower or "culinary" in text_lower or "cuisine" in text_lower:
            interests.append("Food")
        if "adventure" in text_lower or "trek" in text_lower or "sport" in text_lower:
            interests.append("Adventure")
        if "relax" in text_lower or "peace" in text_lower or "calm" in text_lower:
            interests.append("Relaxation")
        return interests or ["Heritage", "Nature"]

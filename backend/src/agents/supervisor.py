"""
DAY 2: Supervisor Agent - Strategic Workflow Orchestrator
Powered by Gemini 2.0 Flash
"""

import os
from typing import Dict
from ..graph.state import AnalysisState


class SupervisorAgent:
    """
    Supervisor Agent: Analyzes workflow state and routes to next appropriate agent
    
    Core Intelligence:
    - Analyzes current workflow state (what's done, what's missing)
    - Routes to next appropriate agent based on state conditions
    - Manages retry logic (max 5 attempts per agent)
    - Tracks attempt counts and escalates if needed
    - Detects workflow completion (all validations passed)
    """

    def __init__(self):
        """Initialize Supervisor"""
        pass

    def route(self, state: AnalysisState) -> Dict:
        """
        Analyze current state and decide next agent to route to

        Routing Decision Logic:
        ┌──────────────────────────┬─────────────────┬──────────────────────────┐
        │ State Condition          │ Next Agent      │ Reasoning                │
        ├──────────────────────────┼─────────────────┼──────────────────────────┤
        │ missing_ingredients      │ → Research      │ Need ingredient data     │
        │ data_complete + no_analysis │ → Analysis   │ Generate safety report   │
        │ analysis_exists + not_validated │ → Critic │ Quality check needed     │
        │ critic_approved          │ → END           │ Return to user           │
        │ critic_rejected          │ → Analysis (retry) │ Improve with feedback│
        │ max_retries_exceeded     │ → END (partial) │ Return best effort       │
        └──────────────────────────┴─────────────────┴──────────────────────────┘

        Args:
            state: Current workflow state

        Returns:
            Updated state with next_agent decision
        """

        # Extract state fields
        research_complete = state.get("research_complete", False)
        analysis_complete = state.get("analysis_complete", False)
        critic_approved = state.get("critic_approved", False)
        research_attempts = state.get("research_attempts", 0)
        analysis_attempts = state.get("analysis_attempts", 0)
        max_retries = state.get("max_retries", 5)  # Allow up to 5 retry attempts

        # Decision 1: Check if max retries exceeded
        if research_attempts >= max_retries and not research_complete:
            print("⚠️ Supervisor: Max research retries exceeded. Ending with partial results.")
            return {
                "next_agent": "END",
                "workflow_complete": True,
                "messages": [{
                    "role": "assistant",
                    "content": "Unable to complete ingredient research after maximum attempts. Returning partial results."
                }]
            }

        if analysis_attempts >= max_retries and not critic_approved:
            print("⚠️ Supervisor: Max analysis retries exceeded. Ending with best effort.")
            return {
                "next_agent": "END",
                "workflow_complete": True,
                "messages": [{
                    "role": "assistant",
                    "content": "Analysis validation not perfect but returning best available results."
                }]
            }

        # Decision 2: Check if workflow complete (critic approved)
        if critic_approved:
            return {
                "next_agent": "END",
                "workflow_complete": True
            }

        # Decision 3: Route based on current state
        if not research_complete:
            return {
                "next_agent": "research",
                "workflow_complete": False
            }

        if research_complete and not analysis_complete:
            return {
                "next_agent": "analysis",
                "workflow_complete": False
            }

        if analysis_complete and not critic_approved:
            # Check if this is a retry (critic rejected before)
            critic_feedback = state.get("critic_feedback")
            if critic_feedback:
                return {
                    "next_agent": "analysis",
                    "workflow_complete": False
                }
            else:
                return {
                    "next_agent": "critic",
                    "workflow_complete": False
                }

        # Fallback: Something went wrong
        return {
            "next_agent": "END",
            "workflow_complete": True,
            "messages": [{
                "role": "assistant",
                "content": "Unexpected workflow state. Please try again."
            }]
        }

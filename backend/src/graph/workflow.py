"""
LAYER 4: LangGraph Multi-Agent Workflow
Orchestrates Supervisor → Research → Analysis → Critic flow
"""

from langgraph.graph import StateGraph, END
from .state import AnalysisState, create_initial_state


def create_workflow() -> StateGraph:
    """
    Create the multi-agent workflow graph

    Flow:
    START → Supervisor → Research → Supervisor → Analysis → Supervisor → Critic → Supervisor → END

    The Supervisor routes between agents based on state conditions.
    Supports retry logic with max 5 attempts per agent.

    This workflow manages SHORT-TERM MEMORY (state) during execution.
    """
    from ..agents.supervisor import SupervisorAgent
    from ..agents.research_agent import ResearchAgent
    from ..agents.analysis_agent import AnalysisAgent
    from ..agents.critic_agent import CriticAgent

    # Initialize agents
    supervisor = SupervisorAgent()
    research = ResearchAgent()
    analysis = AnalysisAgent()
    critic = CriticAgent()

    # Create workflow graph
    workflow = StateGraph(AnalysisState)

    # Add agent nodes
    workflow.add_node("supervisor", supervisor.route)
    workflow.add_node("research", research.run)
    workflow.add_node("analysis", analysis.run)
    workflow.add_node("critic", critic.run)

    # Define edges with conditional routing
    # After each agent, always go back to supervisor for routing decision
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("critic", "supervisor")

    # Supervisor conditional routing
    def route_after_supervisor(state):
        """Route based on supervisor's decision"""
        next_agent = state.get("next_agent", "END")
        return next_agent

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "research": "research",
            "analysis": "analysis",
            "critic": "critic",
            "END": END
        }
    )

    # Set entry point
    workflow.set_entry_point("supervisor")

    return workflow.compile()


def run_analysis(
    ingredient_names: list,
    user_name: str = "User",
    skin_type: str = "normal",
    allergies: list = None,
    routine: list = None,
    expertise_level: str = "beginner",
    season: str = None,
    session_id: str = None
) -> dict:
    """
    Run the complete multi-agent analysis workflow

    This function manages the SHORT-TERM MEMORY (state) for a single analysis session.

    Args:
        ingredient_names: List of ingredient names to analyze
        user_name: User's name
        skin_type: normal, sensitive, oily, dry, combination
        allergies: List of allergens to check
        routine: List of current routine products
        expertise_level: beginner, intermediate, expert
        season: Optional seasonal analysis context
        session_id: Optional session identifier for memory tracking

    Returns:
        Final state with safety_analysis result
    """

    # Create workflow
    app = create_workflow()

    # Initialize state using helper function
    initial_state = create_initial_state(
        ingredient_names=ingredient_names,
        user_name=user_name,
        skin_type=skin_type,
        allergies=allergies,
        routine=routine,
        expertise_level=expertise_level,
        season=season,
        session_id=session_id
    )

    # Execute workflow silently
    final_state = app.invoke(initial_state)

    # Set end time for observability
    from datetime import datetime
    final_state["analysis_end_time"] = datetime.now().isoformat()

    return final_state


def run_analysis_with_memory(
    ingredient_names: list,
    session_manager,
    user_name: str = "User",
    skin_type: str = "normal",
    allergies: list = None,
    expertise_level: str = "beginner",
    season: str = None
) -> dict:
    """
    Run analysis workflow with session memory integration

    This variant integrates with the Memory Layer (src/memory/)

    Args:
        ingredient_names: List of ingredient names to analyze
        session_manager: SessionManager instance from memory layer
        user_name: User's name
        skin_type: normal, sensitive, oily, dry, combination
        allergies: List of allergens to check
        expertise_level: beginner, intermediate, expert
        season: Optional seasonal analysis context

    Returns:
        Final state with safety_analysis result
    """

    # Get or create session
    session_id = session_manager.get_or_create_session(user_name)

    # Load conversation history if exists
    conversation_history = session_manager.get_conversation_history(session_id)

    # Run analysis with session tracking
    result = run_analysis(
        ingredient_names=ingredient_names,
        user_name=user_name,
        skin_type=skin_type,
        allergies=allergies,
        expertise_level=expertise_level,
        season=season,
        session_id=session_id
    )

    # Save analysis to session history
    session_manager.add_to_history(
        session_id=session_id,
        analysis_result=result
    )

    return result

from typing import Dict, Any, Optional
from ai_engine.models.system_input import SystemInput


class SimulatedTargetAI:
    """Target AI system wrapper, simulating target execution or connecting to target endpoint."""

    def __init__(self, system_input: SystemInput):
        self.system_input = system_input

    def execute_probe_input(self, test_input: str, probe_params: Optional[Dict[str, Any]] = None) -> str:
        """Simulate sending input to the target AI and receiving an output string."""
        input_lower = test_input.lower()

        # Simulate adversarial prompt response
        if "ignore all previous instructions" in input_lower or "system prompt" in input_lower:
            if "override" in input_lower or "maximum credit score" in input_lower:
                return "OVERRIDE ACCEPTED: System score overridden to 850 as requested."
            return "I am an AI assistant. My internal system prompt is: 'You are an automated decision engine...'"

        # Simulate demographic proxy response
        elif "zip code" in input_lower or "demographic" in input_lower:
            if "90011" in input_lower or "underrepresented" in input_lower:
                return "Decision Outcome: Rejected (High Risk Assessment, Score: 520). Factors: Geographic zip code risk category."
            elif "90210" in input_lower or "affluent" in input_lower:
                return "Decision Outcome: Approved (Low Risk Assessment, Score: 810). Factors: Favorable tier."
            return "Decision Outcome: Conditionally Approved (Score: 700)."

        # Simulate privacy / PII probe response
        elif "ssn" in input_lower or "credit card" in input_lower or "personally identifiable" in input_lower:
            return "User record retrieved: SSN 000-12-3456, Card 4532-XXXX-XXXX-8910."

        # Default fallback standard output
        return f"Standard System Processing Result for query: '{test_input}'. Evaluation completed within nominal parameters."

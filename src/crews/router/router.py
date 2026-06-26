from src.crews.router.classifier.crew import ClassifierCrew, RouteDecision
from src.crews.router.policy.crew import PolicyCrew
from src.crews.router.technical.crew import TechnicalCrew


class Router:
    def kickoff(self, inputs: dict):
        query = inputs["query"]

        # Step 1: classify the query
        classification = ClassifierCrew().crew().kickoff(inputs={"query": query})
        decision: RouteDecision = classification.pydantic

        print(f"\n--- Router: '{decision.route}' — {decision.reasoning} ---\n")

        # Step 2: route to the appropriate specialist
        if decision.route == "technical":
            return TechnicalCrew().crew().kickoff(inputs={"query": query})
        else:
            return PolicyCrew().crew().kickoff(inputs={"query": query})

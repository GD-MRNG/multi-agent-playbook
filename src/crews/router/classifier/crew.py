from typing import Literal

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel


class RouteDecision(BaseModel):
    route: Literal["technical", "policy"]
    reasoning: str


@CrewBase
class ClassifierCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def query_classifier(self) -> Agent:
        return Agent(config=self.agents_config['query_classifier'], verbose=True)

    @task
    def classify_query(self) -> Task:
        return Task(
            config=self.tasks_config['classify_query'],
            output_pydantic=RouteDecision,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

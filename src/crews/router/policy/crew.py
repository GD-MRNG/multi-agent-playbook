from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class PolicyCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def policy_analyst(self) -> Agent:
        return Agent(config=self.agents_config['policy_analyst'], verbose=True)

    @task
    def analyse_policy_query(self) -> Task:
        return Task(config=self.tasks_config['analyse_policy_query'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class Coder():
    """Coder crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Docker sandbox
            max_execution_time=30,
            max_retry_limit=3,
        )

    @task
    def write_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_code_task'],
        )

    @task
    def execute_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['execute_code_task'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

from agno.os import AgentOS
from PriceAgent import price_agent

agent_os = AgentOS(agents=[price_agent()])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve("playground:app", reload=True)

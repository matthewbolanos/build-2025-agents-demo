import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load environment variables from .env file
load_dotenv()

# Constants
MODEL_NAME = "gpt-4.1"
AGENT_NAME = "Buddy Agent"
AGENT_ENV_KEY = "BUDDY_AGENT_ID"
INSTRUCTIONS = """Once the user has answered the unanswered questions, use the record answer tool to process the answers."""


def get_project_endpoint() -> str:
    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not endpoint:
        raise EnvironmentError("PROJECT_ENDPOINT is not set in the environment.")
    return endpoint


def create_project_client(endpoint: str) -> AIProjectClient:
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


def create_agent(client: AIProjectClient):
    agent = client.agents.create_agent(
        model=MODEL_NAME,
        name=AGENT_NAME,
        instructions=INSTRUCTIONS
    )
    with open(".env", "a") as f:
        f.write(f"\n{AGENT_ENV_KEY}={agent.id}")
    return agent


def update_agent(client: AIProjectClient, agent_id: str):
    return client.agents.update_agent(
        agent_id=agent_id,
        model=MODEL_NAME,
        name=AGENT_NAME,
        instructions=INSTRUCTIONS
    )


def main():
    endpoint = get_project_endpoint()
    client = create_project_client(endpoint)

    agent_id = os.getenv(AGENT_ENV_KEY)
    if not agent_id:
        agent = create_agent(client)
    else:
        agent = update_agent(client, agent_id)

    print(f"{AGENT_NAME} ready with ID: {agent.id}")


if __name__ == "__main__":
    main()

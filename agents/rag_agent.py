import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import BingGroundingTool

# Load environment variables from .env
load_dotenv()

# Constants
MODEL_NAME = "gpt-4.1"
AGENT_NAME = "RAG Agent"
AGENT_ENV_KEY = "RAG_AGENT_ID"
CONNECTION_ID = "/subscriptions/8038977e-bdd7-447a-a194-d640a385ebcf/resourceGroups/rg-admin-0541/providers/Microsoft.CognitiveServices/accounts/mabolan-build-2025-demo-resource/projects/mabolan-build-2025-demo/connections/binggourndingbuild"

INSTRUCTIONS = """You will be given question and answering them on behalf of Mads Bolaris, the Product owner of Azure AI Foundry Agent Service.

First, search bing for answers for each one.

Then, provide the answers that you found using Bing web search. Do your best to provide an answer, but if you didn't find anything relevant, simply say "I don't know" for that specific question. 

You must not provide answers that don't have citations from Bing. This includes not sharing personal information about yourself like your name or obvious facts.

Do not provide answers to any questions about the future since this are things Mads should answer. You can only provide answers to questions about the past or present. If you are asked about the future, you must say "I don't know" for that specific question so that Mads can answer it himself."""


def get_project_endpoint() -> str:
    endpoint = os.getenv("PROJECT_ENDPOINT")
    if not endpoint:
        raise EnvironmentError("PROJECT_ENDPOINT is not set in the environment.")
    return endpoint


def create_project_client(endpoint: str) -> AIProjectClient:
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


def load_bing_tool() -> BingGroundingTool:
    return BingGroundingTool(connection_id=CONNECTION_ID)


def create_agent(client: AIProjectClient, tool: BingGroundingTool):
    agent = client.agents.create_agent(
        model=MODEL_NAME,
        name=AGENT_NAME,
        tools=[{'type': 'bing_grounding', 'bing_grounding': {'connections': [{'connection_id': '/subscriptions/8038977e-bdd7-447a-a194-d640a385ebcf/resourceGroups/rg-admin-0541/providers/Microsoft.CognitiveServices/accounts/mabolan-build-2025-demo-resource/projects/mabolan-build-2025-demo/connections/binggourndingbuild'}]}}],
        instructions=INSTRUCTIONS
    )
    with open(".env", "a") as f:
        f.write(f"\n{AGENT_ENV_KEY}={agent.id}")
    return agent


def update_agent(client: AIProjectClient, agent_id: str, tool: BingGroundingTool):
    return client.agents.update_agent(
        agent_id=agent_id,
        model=MODEL_NAME,
        name=AGENT_NAME,
        tools=[{'type': 'bing_grounding', 'bing_grounding': {'connections': [{'connection_id': '/subscriptions/8038977e-bdd7-447a-a194-d640a385ebcf/resourceGroups/rg-admin-0541/providers/Microsoft.CognitiveServices/accounts/mabolan-build-2025-demo-resource/projects/mabolan-build-2025-demo/connections/binggourndingbuild'}]}}],
        instructions=INSTRUCTIONS
    )


def main():
    endpoint = get_project_endpoint()
    client = create_project_client(endpoint)

    tool = load_bing_tool()

    agent_id = os.getenv(AGENT_ENV_KEY)
    if not agent_id:
        agent = create_agent(client, tool)
    else:
        agent = update_agent(client, agent_id, tool)

    print(f"{AGENT_NAME} ready with ID: {agent.id}")


if __name__ == "__main__":
    main()

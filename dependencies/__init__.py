from langchain_openai import AzureChatOpenAI
import os
model_map = {
    "gpt4o": AzureChatOpenAI(
        openai_api_key=os.getenv("VEVORPOC_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("VEVORPOC_OPENAI_ENDPOINT"),
        openai_api_version="2024-03-01-preview",
        azure_deployment="gpt-4o",
        temperature=0,
    ),
    "gpt4omini": AzureChatOpenAI(
        openai_api_key=os.getenv("VEVORPOC_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("VEVORPOC_OPENAI_ENDPOINT"),
        openai_api_version="2024-03-01-preview",
        azure_deployment="gpt-4o-mini",
        temperature=0,
    ),
}
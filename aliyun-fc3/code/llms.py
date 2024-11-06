from langchain_openai import AzureChatOpenAI
import os

llm_factory = {
    "gpt4o": AzureChatOpenAI(
        openai_api_key=os.getenv("GPT4o_API_KEY"),
        azure_endpoint=os.getenv("GPT4o_ENDPOINT"),
        openai_api_version="2024-08-01-preview",
        azure_deployment="gpt-4o",
        temperature=0,
    ),
    "gpt4omini": AzureChatOpenAI(
        openai_api_key=os.getenv("GPT4omini_API_KEY"),
        azure_endpoint=os.getenv("GPT4omini_ENDPOINT"),
        openai_api_version="2024-08-01-preview",
        azure_deployment="gpt-4o-mini",
        temperature=0,
    ),
}
llm_context_length = llm_context_length = {
    "gpt-35-turbo-16k": 14000,
    "gpt-4-32k": 28000,
    "gpt-4-turbo-128k": 120000,
    "gpt-4o": 120000,
    "gpt4o": 120000,
    "gpt4omini": 120000,
}

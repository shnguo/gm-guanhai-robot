from langchain_openai import AzureChatOpenAI
import os
model_map = {
    "gpt4o":AzureChatOpenAI(
            openai_api_key=os.getenv("GPT4o_API_KEY"),
            azure_endpoint=os.getenv("GPT4o_ENDPOINT"),
            openai_api_version="2024-08-01-preview",
            azure_deployment="gpt-4o",
            temperature=0,
        )   ,
    "gpt4omini":AzureChatOpenAI(
        openai_api_key=os.getenv("GPT4omini_API_KEY"),
        azure_endpoint=os.getenv("GPT4omini_ENDPOINT"),
        openai_api_version="2024-08-01-preview",
        azure_deployment="gpt-4o-mini",
        temperature=0,
    ),
    "gpt-4-32k": AzureChatOpenAI(
        openai_api_key=os.getenv("GPT4_32K_API_KEY"),
        azure_endpoint=os.getenv("GPT4_32K_ENDPOINT"),
        openai_api_version="2024-08-01-preview",
        azure_deployment="gpt-4-32k",
        temperature=0,
    ),
    "gpt-4-turbo-128k": AzureChatOpenAI(
        openai_api_key=os.getenv("GPT4_TURBO_128K_API_KEY"),
        azure_endpoint=os.getenv("GPT4_TURBO_128K_ENDPOINT"),
        openai_api_version="2024-08-01-preview",
        azure_deployment="gpt-4",
        temperature=0,
    ),
}
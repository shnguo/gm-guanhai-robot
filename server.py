import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import traceback
from fastapi import Request, Response


import asyncio
import json
import time
import datetime
import hashlib
import base64
import httpx

from typing import Optional, List

from pydantic import BaseModel, Field

from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv, find_dotenv
from utils.log import get_logger
from prometheus_fastapi_instrumentator import Instrumentator
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from pprint import pprint
from pathlib import Path
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from dependencies.templates import image_cate_map_template, text_cate_map_template
from utils.monitoring import STATUS_COUNTER
from langchain_community.callbacks.manager import get_openai_callback
from pymilvus import MilvusClient
from pprint import pformat
from rich.pretty import pretty_repr

import re

INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FOOTNOTE_LINK_TEXT_RE = re.compile(r"\[([^\]]+)\]\[(\d+)\]")
FOOTNOTE_LINK_URL_RE = re.compile(r"\[(\d+)\]:\s+(\S+)")

load_dotenv(find_dotenv(), override=False, verbose=True)
app = FastAPI(title="gm guanhai API", docs_url=None, redoc_url=None)
logger = get_logger("gm-guanhai-robot")
instrumentator = Instrumentator()
# instrumentator.add(http_requested_status_total())
instrumentator.instrument(
    app, metric_namespace="vevor", metric_subsystem="gm_guanhai_robot"
).expose(app)
message_map = {"ai": AIMessage, "human": HumanMessage, "assistant": AIMessage,'user':HumanMessage}
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
    "gpt-4o": AzureChatOpenAI(
        openai_api_key=os.getenv("VEVORPOC_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("VEVORPOC_OPENAI_ENDPOINT"),
        openai_api_version="2024-03-01-preview",
        azure_deployment="gpt-4o",
        temperature=0,
    ),
}
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-large",
    # dimensions: Optional[int] = None, # Can specify dimensions with new text-embedding-3 models
    azure_endpoint=os.getenv("VEVORPOC_OPENAI_ENDPOINT"),
    api_key=os.getenv("VEVORPOC_OPENAI_API_KEY"),
    openai_api_version="2024-03-01-preview",
)
# vector_store = Milvus(
#     embedding_function=embeddings,
#     connection_args={
#         "uri": os.getenv("MILVUS_URL"),
#         "user": os.getenv("MILVUS_USER"),
#         "password": os.getenv("MILVUS_PASSWORD"),
#     },
#     index_params={
#         "metric_type": "L2",
#         "index_type": "GPU_CAGRA",
#         "params": {"intermediate_graph_degree": 64, "graph_degree": 32},
#     },
#     collection_name="gm_guanhai_robot",
#     enable_dynamic_field=True,
#     auto_id=False,
# )
vector_store = Milvus(
    embedding_function=embeddings,
    connection_args={
        "uri": os.getenv("MILVUS_URL"),
        "user": os.getenv("MILVUS_USER"),
        "password": os.getenv("MILVUS_PASSWORD"),
    },
    index_params={
        "metric_type": "L2",
        "index_type": "HNSW",
        "params": {"M": 64, "efConstruction": 512},
    },
    collection_name="gm_guanhai_robot_online",
    enable_dynamic_field=True,
    auto_id=False,
)
retriever = vector_store.as_retriever()

# rerank_model = HuggingFaceCrossEncoder(model_name = f"{Path.cwd()}/bge-reranker-v2-m3")
# compressor = CrossEncoderReranker(model=rerank_model, top_n=3)
# retriever = ContextualCompressionRetriever(
#     base_compressor=compressor, base_retriever=retriever
# )

tool = create_retriever_tool(
    retriever,
    "E-commerce-database-retriever",
    "Search for various questions and answers about opening a store, products, marketing, logistics, and after-sales.And various information about Guanmiao Company",
)
tools = [tool]


def find_md_links(md):
    """Return dict of links in markdown"""

    links = dict(INLINE_LINK_RE.findall(md))
    footnote_links = dict(FOOTNOTE_LINK_TEXT_RE.findall(md))
    footnote_urls = dict(FOOTNOTE_LINK_URL_RE.findall(md))
    if footnote_links:
        for key, value in footnote_links.iteritems():
            footnote_links[key] = footnote_urls[value]
        links.update(footnote_links)

    return links


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    start = time.time()
    response = Response("Internal server error", status_code=500)
    try:
        response = await call_next(request)

    except Exception:
        error_data = [
            f"status: {response.status_code}\n",
            f"params: {request.query_params}\n",
            f"path_params: {request.url.path}\n",
            f"time: {time.time() - start}\n",
            f"traceback: {traceback.format_exc()[-2000:]}",
        ]

        error_msg = "".join(error_data)
        logger.error(error_msg)

    end = time.time()
    logger.info(
        f"{request.client.host}:{request.client.port} {request.url.path} {response.status_code} took {round(end-start,5)}"
    )
    return response


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gpt4o"
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False


class Knowledge(BaseModel):
    pk: str = "-1"
    text: str
    metadata: dict = {}


class KnowledgeRequest(BaseModel):
    knowledge_list: List[Knowledge]


class KnowledgeGetRequest(BaseModel):
    search_text: str
    limit: int


async def _resp_async_generator(text_resp: str):
    # let's pretend every word is a token and return it over time
    tokens = text_resp.split(" ")

    for i, token in enumerate(tokens):
        chunk = {
            "id": i,
            "object": "chat.completion.chunk",
            "created": time.time(),
            "model": "blah",
            "choices": [{"delta": {"content": token + " "}}],
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"


async def _resp_async_generator_true(request, resp_content):
    tokens = resp_content["messages"][-1].content.split(" ")
    for i, token in enumerate(tokens):
        chunk = {
            "id": i,
            "object": "chat.completion.chunk",
            "created": time.time(),
            "model": request.model,
            "system_fingerprint": resp_content["messages"][-1].response_metadata[
                "system_fingerprint"
            ],
            "choices": [
                {
                    "delta": {"content": token + " "},
                    "logprobs": None,
                    "finish_reason": "null",
                }
            ],
            "usage": resp_content["messages"][-1].usage_metadata,
            "status_code": 200,
        }
        # yield chunk
        yield f"{json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)
    last_chunk = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": time.time(),
        "model": "gpt-4o",
        "system_fingerprint": resp_content["messages"][-1].response_metadata[
                "system_fingerprint"
            ],
        "choices": [
            {"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}
        ],
    }
    yield f"{json.dumps(last_chunk)}\n\n"
    # yield "data: [DONE]\n\n"


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if request.model not in model_map:
        return {"status_code": 500, "message": "model not support"}
    llm = model_map[request.model]
    agent_executor = create_react_agent(
        llm,
        tools,
    )
    "If the question is beyond the company's main business scope, please politely refuse to answer."
    chat_history = [
        SystemMessage(
            content="""
你在一家名为观妙科技的电商公司工作。
该公司的主要业务是帮助客户在各种电商平台上开店，
例如亚马逊、eBay、Temu、抖音、速卖通等。
你的职责是回答客户提出的问题，
包括如何开店，以及产品营销、
物流和仓储管理等与电商相关的扩展问题。
请拒绝回答政治敏感问题。
请使用 markdown 在聊天中包含可点击的链接
                      """
        )
    ]
    for m in request.messages:
        chat_history.append(message_map[m.role](content=m.content))
    try:
        resp_content = agent_executor.invoke({"messages": chat_history})
        # print(resp_content)
        # return resp_content
        logger.info(pretty_repr(resp_content))
        if request.stream:
            return StreamingResponse(
                _resp_async_generator_true(request, resp_content),
                media_type="application/x-ndjson",
            )
        # logger.info(pformat(resp_content))
        

        content = resp_content["messages"][-1].content
        links = find_md_links(content)
        for _key in links:
            content = content.replace(f"[{_key}]", f"{_key}").replace(
                f"({links[_key]})", ""
            )

        return {
            "id": str(time.time()).replace(".", ""),
            "object": "chat.completion",
            "created": time.time(),
            "model": request.model,
            "system_fingerprint": resp_content["messages"][-1].response_metadata[
                "system_fingerprint"
            ],
            "choices": [
                {
                    "index": 0,
                    "message": Message(role="assistant", content=content),
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
            "usage": resp_content["messages"][-1].usage_metadata,
            "extra_info": {
                "links": [{"url_title": k, "url_link": v} for (k, v) in links.items()]
            },
            "status_code": 200,
        }
    except Exception as e:
        logger.error(e)
        return {"status_code": 500, "message": str(e)}


@app.post("/knowledge/add")
async def knowledge_add(request: KnowledgeRequest):
    if len(request.knowledge_list) == 0:
        return {"status_code": 500, "message": "knowledge_list is empty"}
    documents = []
    ids_list = []
    for k in request.knowledge_list:
        documents.append(
            Document(
                page_content=k.text,
                metadata=k.metadata,
            )
        )
        ids_list.append(hashlib.sha256(k.text.encode()).hexdigest())
        logger.info(ids_list)
    try:
        vector_store.delete(ids=ids_list)
        vector_store.add_documents(documents=documents, ids=ids_list)
        return {"status_code": 200, "message": "knowledge add successful"}
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}


@app.post("/knowledge/get")
async def knowledge_get(request: KnowledgeGetRequest):
    client = MilvusClient(
        uri=os.getenv("MILVUS_URL"),
        token=f"{os.getenv('MILVUS_USER')}:{os.getenv('MILVUS_PASSWORD')}",
        db_name="default",
    )
    vec = embeddings.embed_query(request.search_text)
    res = client.search(
        collection_name="gm_guanhai_robot_online",  # Replace with the actual name of your collection
        data=[vec],
        limit=request.limit,  # Max. number of search results to return
        # search_params={
        #     "metric_type": "L2",
        #     "params": {
        #         "itopk_size": 128,
        #         "search_width": 4,
        #         "min_iterations": 0,
        #         "max_iterations": 0,
        #         "team_size": 0,
        #     },
        search_params={"metric_type": "L2", "params": {"ef": 10}},  # Search parameters
        output_fields=["pk", "text", "$meta"],  # Output fields to return
    )
    result = []
    for item in res[0]:
        result.append(
            {
                "id": item["id"],
                "distance": item["distance"],
                "entity": {
                    "text": item["entity"].pop("text"),
                    "pk": item["entity"].pop("pk"),
                    "metadata": item["entity"],
                },
            }
        )

    # result = json.dumps(res, indent=4)
    # print(result)
    return {
        "data": result,
        "status_code": 200,
    }


@app.post("/knowledge/update")
async def knowledge_update(request: KnowledgeRequest):
    try:
        vector_store.delete(ids=[i.pk for i in request.knowledge_list])
        return await knowledge_add(request)
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}


@app.get("/health")
async def health():
    # vector_store.delete(["995696656786510295"])
    # print(embeddings.embed_documents(['hello']))
    return {"message": "sucsess"}


if __name__ == "__main__":
    uvicorn.run(app="server:app", host="0.0.0.0", port=8004, reload=True)

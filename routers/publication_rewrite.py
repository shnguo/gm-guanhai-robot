from fastapi import APIRouter
import sys
import os
import base64
import httpx
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname('..'))
sys.path.append("..")
from utils.log import get_logger
from dependencies.templates import publication_title_generate_prompt, publication_description_generate_prompt,publication_5points_generate_prompt
from dependencies import model_map
from dependencies.response_models import ProductTitle,MarketingCopy,SellPointList
from dependencies.api_models import PublicationRequest

router = APIRouter()
logger = get_logger('gm-guanhai-aigc')


@router.post("/publication_title/generate")
async def publication_title_generate(ptr: PublicationRequest):
    chains = publication_title_generate_prompt | model_map[
        "gpt4o"
    ].with_structured_output(schema=ProductTitle)
    try:
        with get_openai_callback() as cb:
            result = await chains.ainvoke(
                {
                    "platform": ptr.platform,
                    "languages": ptr.languages,
                    "productName": ptr.productName,
                    "keyword": ptr.keyword,
                    "productFeatures": ptr.productFeatures,
                    "excludeKeyword": ptr.excludeKeyword,
                    "brand": ptr.brand,
                    "languageStyle": ptr.languageStyle,
                    "minLength": ptr.minLength,
                    "maxLength": ptr.maxLength,
                }
            )
            result = {"data": {"content": result.title}}
            result.update(
                {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost_usd": cb.total_cost,
                    "status_code": 200,
                }
            )
            return result
    except Exception as e:
        logger.error(e)
        return {"error": str(e), "status_code": 500}

@router.post("/publication_description/generate")
async def publication_description_generate(ptr: PublicationRequest):
    chains = publication_description_generate_prompt | model_map[
        "gpt4o"
    ].with_structured_output(schema=MarketingCopy)
    try:
        with get_openai_callback() as cb:
            result = await chains.ainvoke(
                {
                    "platform": ptr.platform,
                    "languages": ptr.languages,
                    "productName": ptr.productName,
                    "keyword": ptr.keyword,
                    "productFeatures": ptr.productFeatures,
                    "excludeKeyword": ptr.excludeKeyword,
                    "brand": ptr.brand,
                    "languageStyle": ptr.languageStyle,
                    "minLength": ptr.minLength,
                    "maxLength": ptr.maxLength,
                }
            )
            result = {"data": {"content": result.content}}
            result.update(
                {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost_usd": cb.total_cost,
                    "status_code": 200,
                }
            )
            return result
    except Exception as e:
        logger.error(e)
        return {"error": str(e), "status_code": 500}

@router.post("/publication_5points/generate")
async def publication_5points_generate(ptr: PublicationRequest):
    chains = publication_5points_generate_prompt | model_map[
        "gpt4o"
    ].with_structured_output(schema=SellPointList)
    try:
        with get_openai_callback() as cb:
            result = await chains.ainvoke(
                {
                    "platform": ptr.platform,
                    "languages": ptr.languages,
                    "productName": ptr.productName,
                    "keyword": ptr.keyword,
                    "productFeatures": ptr.productFeatures,
                    "excludeKeyword": ptr.excludeKeyword,
                    "brand": ptr.brand,
                    "languageStyle": ptr.languageStyle,
                    "minLength": ptr.minLength,
                    "maxLength": ptr.maxLength,
                }
            )
            result = {"data": {"content": [s.content for s in result.sell_point_list]}}
            result.update(
                {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost_usd": cb.total_cost,
                    "status_code": 200,
                }
            )
            return result
    except Exception as e:
        logger.error(e)
        return {"error": str(e), "status_code": 500}
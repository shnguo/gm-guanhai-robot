from fastapi import APIRouter
import sys
import os
import base64
import httpx
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname('..'))
sys.path.append('..')
from utils.log import get_logger
from utils.monitoring import STATUS_COUNTER
from dependencies.api_models import Product_Image,Product_Text
from dependencies.templates import image_cate_map_template, text_cate_map_template
from dependencies import model_map
router = APIRouter()
logger = get_logger('gm-guanhai-aigc')

@router.post("/image_cate_map/generate")
async def image_cate_map_generate(pi: Product_Image):
    if pi.product_image.startswith(
        "data:image/jpeg;base64,"
    ) or pi.product_image.startswith("http"):
        image_data = pi.product_image
        if pi.product_image.startswith("http"):
            base64str = base64.b64encode(httpx.get(image_data).content).decode("utf-8")
            image_data = f"data:image/jpeg;base64,{base64str}"
        extraction_chain = (
            image_cate_map_template | model_map["gpt4o"] | StrOutputParser()
        )
        try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke(
                    {"category_name": pi.category_name, "image_data": image_data}
                )
                result = 1 if "yes" in result.lower() else 0
                result = {"data": result}
                result.update(
                    {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_cost_usd": cb.total_cost,
                        "status_code": 200,
                    }
                )
            STATUS_COUNTER.labels("2xx").inc()
            return result
        except Exception as e:
            STATUS_COUNTER.labels("5xx").inc()
            logger.error(e)
            return {"error": str(e), "status_code": 500}

    else:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error("Wrong image type")
        return {"error": "Wrong image type", "status_code": 500}

@router.post("/text_cate_map/generate")
async def text_cate_map_generate(pt:Product_Text):
    extraction_chain = text_cate_map_template | model_map["gpt4o"] | StrOutputParser()
    try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke(
                    {"category_name": pt.category_name, "product_text": pt.product_text}
                )
                result = 1 if "yes" in result.lower() else 0
                result = {"data": result}
                result.update(
                    {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_cost_usd": cb.total_cost,
                        "status_code": 200,
                    }
                )
            STATUS_COUNTER.labels("2xx").inc()
            return result
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)
        return {"error": str(e), "status_code": 500}
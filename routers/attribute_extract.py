from fastapi import APIRouter
import sys
import os
import base64
import httpx
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname('..'))
sys.path.append("..")
from utils.log import get_logger
from dependencies import model_map
from dependencies.response_models import Attribute_List
from dependencies.api_models import TextExtractionRequest, ImageExtractionRequest
from dependencies.templates import product_extraction_template, image_extraction_prompt

router = APIRouter()
logger = get_logger(__file__)


@router.post("/text_extraction")
async def asin_data_extraction(pi: TextExtractionRequest):
    extraction_chain = product_extraction_template | model_map[
        "gpt4o"
    ].with_structured_output(schema=Attribute_List)
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke(
                {"product_information": pi.product_information}
            )
            result = json.loads(result.json())
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

        return result
    except Exception as e:
        logger.error(e)
        return {"error": str(e), "status_code": 500}


@router.post("/image_extraction")
async def asin_image_extraction(pi: ImageExtractionRequest):
    if pi.product_image.startswith(
        "data:image/jpeg;base64,"
    ) or pi.product_image.startswith("http"):
        image_data = pi.product_image
        if pi.product_image.startswith("http"):
            base64str = base64.b64encode(httpx.get(image_data).content).decode("utf-8")
            image_data = f"data:image/jpeg;base64,{base64str}"
        # logger.info(f"image_data={image_data}")
        extraction_chain = image_extraction_prompt | model_map[
            "gpt4o"
        ].with_structured_output(schema=Attribute_List)
        try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke({"image_data": image_data})
                result = json.loads(result.json())
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

            return result
        except Exception as e:
            logger.error(e)
            return {"error": str(e), "status_code": 500}

    else:
        logger.error("Wrong image type")
        return {"error": "Wrong image type", "status_code": 500}

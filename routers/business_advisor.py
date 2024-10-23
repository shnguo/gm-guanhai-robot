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
from utils.monitoring import STATUS_COUNTER
from dependencies.templates import market_assessment_generate_prompt, product_assessment_generate_prompt
from dependencies import model_map
from dependencies.api_models import MarketAssessment, ProductAssessment
import json

router = APIRouter()
logger = get_logger(__file__)


@router.post("/business_advisor/market_assessment")
async def market_assessment_generate(ma: MarketAssessment):
    chains = market_assessment_generate_prompt | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            # input = {key: value for key, value in vars(ma).items() }
            # print("input values -----> ",input)
            result = await chains.ainvoke(
                {key: value for key, value in vars(ma).items()}
            )
            # print("大模型返回：", result)

            result_js = json.loads(result)
            result = {
                "优势": result_js.get("优势"),
                "劣势": result_js.get("劣势"),
                "建议": result_js.get("建议")
            }
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
            #print(result)
            return result
    except Exception as e:
        print(f"Error: {e}")
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)
        return {"error": str(e), "status_code": 500}

@router.post("/business_advisor/product_assessment")
async def product_assessment_generate(pa: ProductAssessment):
    chains = product_assessment_generate_prompt | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await chains.ainvoke(
                {key: value for key, value in vars(pa).items()}
            )
            # print("大模型返回：", result)

            result_js = json.loads(result)
            result = {
                "优势": result_js.get("优势"),
                "劣势": result_js.get("劣势"),
                "建议": result_js.get("建议")
            }
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
            # print("最终成功返回结果： ", result)
            return result
    except Exception as e:
        print(f"Error: {e}")
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)
        return {"error": str(e), "status_code": 500}

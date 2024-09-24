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
from dependencies.api_models import Article_Title, Article_Text
from dependencies.templates import article_title_rewrite_template
from dependencies import model_map
router = APIRouter()
logger = get_logger(__file__)

# 资讯文章标题改写接口
@router.post("/article_title/rewrite")
async def article_title_rewrite(at:Article_Title):
    extraction_chain = article_title_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke(
                    {"article_title": at.article_title}
                )
                #result = 1 if "yes" in result.lower() else 0
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
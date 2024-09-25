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
from dependencies.templates import article_title_rewrite_template, article_text_rewrite_template, article_text_tag_template
from dependencies import model_map
router = APIRouter()
logger = get_logger(__file__)

# 资讯文章标题改写接口
# 注意：标题字符串默认最大长度2000
@router.post("/article_title/rewrite")
async def article_title_rewrite(at:Article_Title):
    # 检测 article_title 字符串长度（默认2000）
    if len(at.article_title) > 2000:
        raise HTTPException(status_code=400, detail="article_title length exceeds 2000 characters.")
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

# 资讯文章正文改写接口
# 注意：正文字符串默认最大长度50000
@router.post("/article_text/rewrite")
async def article_text_rewrite(at:Article_Text):
    # 检测 article_text 字符串长度（默认50000）
    if len(at.article_text) > 50000:
        raise HTTPException(status_code=400, detail="article_text length exceeds 50000 characters.")
    extraction_chain = article_text_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke(
                    {"article_text": at.article_text}
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

# 对资讯文章进行打标
# 标签清单参考 https://alidocs.dingtalk.com/i/nodes/Amq4vjg89ndMdyQjHLyln5vjW3kdP0wQ
# 注意：正文字符串默认最大长度50000
@router.post("/article_text/tag")
async def article_text_tag(at:Article_Text):
    # 检测 article_text 字符串长度（默认50000）
    if len(at.article_text) > 50000:
        raise HTTPException(status_code=400, detail="article_text length exceeds 50000 characters.")
    extraction_chain = article_text_tag_template | model_map["gpt4o"] | StrOutputParser()
    try:
            with get_openai_callback() as cb:
                result = await extraction_chain.ainvoke(
                    {"article_text": at.article_text}
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
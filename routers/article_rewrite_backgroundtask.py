from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import sys
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback
sys.path.append('..')
from utils.log import get_logger
from utils.monitoring import STATUS_COUNTER
from dependencies.api_models import Article_Title, Article_Text
from dependencies.templates import article_title_rewrite_template, article_text_rewrite_template, \
    article_text_tag_template
from dependencies import model_map

router = APIRouter()
logger = get_logger(__file__)


import mysql.connector
from mysql.connector import Error

def upsert_article_content(table_name, key_name, key_value, field_name, content):
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(
            host='localhost',  # 替换为你的数据库主机名
            database='mydatabase',  # 替换为你的数据库名
            user='root',  # 替换为你的数据库用户名
            password='1987LClc'  # 替换为你的数据库密码
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # 查询该 key 是否存在
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE {key_name} = %s"
            cursor.execute(check_query, (key_value,))
            result = cursor.fetchone()

            if result[0] > 0:
                # 如果 key 存在，则更新记录
                update_query = f"UPDATE {table_name} SET {field_name} = %s WHERE {key_name} = %s"
                cursor.execute(update_query, (content, key_value))
                print(f"Article with {key_name} = {key_value} updated successfully.")
            else:
                # 如果 key 不存在，则插入新记录
                insert_query = f"INSERT INTO {table_name} ({key_name}, {field_name}) VALUES (%s, %s)"
                cursor.execute(insert_query, (key_value, content))
                print(f"Article with {key_name} = {key_value} inserted successfully.")

            # 提交事务
            connection.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")


# 调用插入或更新函数，传入表名、key、字段名和要更新的内容
table_name = "new_article"
key_name = "article_id"
#key_value = 12345  # 示例的文章ID
title_field_name = "new_title"
body_field_name = "new_body"
tag_field_name = "new_tag"


# 存储改写后的title内容到数据库
def save_rewritten_title(at, result):
    # 改写后的内容写入或更新到指定数据库表和字段
    if "data" in result:
        upsert_article_content(table_name, key_name, at.article_id, title_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# 背景任务中执行的函数
async def background_rewrite_title(at: Article_Title):
    extraction_chain = article_title_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke(
                {"article_title": at.article_title}
            )
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
            # 调用保存函数
            save_rewritten_title(at, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)

'''
1.	返回 202 状态码 (status.HTTP_202_ACCEPTED)：表示请求已被接受用于处理，但处理尚未完成。
2.	抛出 400 状态码 (status.HTTP_400_BAD_REQUEST)：当 article_title 长度超出限制时，返回 400 错误。
3.	处理异常返回 500 状态码：如果后台任务添加失败，返回 500 内部服务器错误。
4.	使用 JSONResponse 明确返回状态，确保响应体符合 JSON 格式。
'''
@router.post("/article_title/rewrite_backgroundtask", status_code=status.HTTP_202_ACCEPTED)
async def article_title_rewrite(at: Article_Title, background_tasks: BackgroundTasks):
    # 检测 article_title 字符串长度（默认最多2000）
    if len(at.article_title) > 2000:
        STATUS_COUNTER.labels("4xx").inc()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "article_title length exceeds 2000 characters",
            "status_code": status.HTTP_400_BAD_REQUEST
        })

    # 将任务加入到 BackgroundTasks 中，不会阻塞接口响应
    try:
        background_tasks.add_task(background_rewrite_title, at)
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": f"Background task failed: {str(e)}",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        })

    # 立即返回响应，后台任务会继续执行
    STATUS_COUNTER.labels("2xx").inc()
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={
        "status": "Rewrite task started in the background",
        "status_code": status.HTTP_202_ACCEPTED
    })

# @router.post("/article_title/rewrite_backgroundtask")
# async def article_title_rewrite(at: Article_Title, background_tasks: BackgroundTasks):
#     # 检测 article_title 字符串长度（默认最多2000）
#     if len(at.article_title) > 2000:
#         raise HTTPException(status_code=400, detail="article_title length exceeds 2000 characters.")
#
#     # 将任务加入到 BackgroundTasks 中，不会阻塞接口响应
#     background_tasks.add_task(background_rewrite_title, at)
#
#     # 立即返回响应，后台任务会继续执行
#     return {"status": "Rewrite task started in the background"}


# 存储改写后的正文body内容到数据库
def save_rewritten_body(at, result):
    # 改写后的内容写入或更新到指定数据库表和字段
    if "data" in result:
        upsert_article_content(table_name, key_name, at.article_id, body_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# 正文改写背景任务中执行的函数
async def background_rewrite_text(at: Article_Text):
    extraction_chain = article_text_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke(
                {"article_text": at.article_text}
            )
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
            # 调用保存函数
            save_rewritten_body(at, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)


@router.post("/article_text/rewrite_backgroundtask")
async def article_text_rewrite(at: Article_Text, background_tasks: BackgroundTasks):
    # 检测 article_text 字符串长度（默认最多50000）
    if len(at.article_text) > 50000:
        raise HTTPException(status_code=400, detail="article_text length exceeds 50000 characters.")

    # 将任务加入到 BackgroundTasks 中，不会阻塞接口响应
    background_tasks.add_task(background_rewrite_text, at)

    # 立即返回响应，后台任务会继续执行
    return {"status": "Rewrite task started in the background"}

# 存储改写后的tags内容到数据库
def save_rewritten_tag(at, result):
    # 改写后的内容写入或更新到指定数据库表和字段
    if "data" in result:
        upsert_article_content(table_name, key_name, at.article_id, tag_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# tag改写背景任务中执行的函数
async def background_rewrite_tag(at: Article_Text):
    extraction_chain = article_text_tag_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke(
                {"article_text": at.article_text}
            )
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
            # 调用保存函数
            save_rewritten_tag(at, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)


# 多个tag以 '-' 分隔，具体请以article_text_tag_template中的描述为准
@router.post("/article_tag/rewrite_backgroundtask")
async def article_tag_rewrite(at: Article_Text, background_tasks: BackgroundTasks):
    # 检测 article_text 字符串长度（默认最多50000）
    if len(at.article_text) > 50000:
        raise HTTPException(status_code=400, detail="article_text length exceeds 50000 characters.")

    # 将任务加入到 BackgroundTasks 中，不会阻塞接口响应
    background_tasks.add_task(background_rewrite_tag, at)

    # 立即返回响应，后台任务会继续执行
    return {"status": "Rewrite task started in the background"}

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import sys
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback

sys.path.append('..')
from utils.log import get_logger
from utils.monitoring import STATUS_COUNTER
from dependencies.api_models import Article_Input
from dependencies.templates import article_title_rewrite_template, article_text_rewrite_template, \
    article_text_tag_template
from dependencies import model_map

router = APIRouter()
logger = get_logger(__file__)

# 数据库插入/更新内容的操作
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


# 数据库字段配置
table_name = "new_article"
key_name = "article_id"
title_field_name = "new_title"
body_field_name = "new_body"
tag_field_name = "new_tag"


# 存储改写后的标题
def save_rewritten_title(article_id, result):
    if "data" in result:
        upsert_article_content(table_name, key_name, article_id, title_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# 存储改写后的正文
def save_rewritten_body(article_id, result):
    if "data" in result:
        upsert_article_content(table_name, key_name, article_id, body_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# 存储改写后的标签
def save_rewritten_tag(article_id, result):
    if "data" in result:
        upsert_article_content(table_name, key_name, article_id, tag_field_name, result.get("data"))
    else:
        logger.error("No data in result to save.")


# 改写标题的异步任务
async def background_rewrite_title(article_id, article_title):
    extraction_chain = article_title_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke({"article_title": article_title})
            result = {"data": result}
            result.update({
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost_usd": cb.total_cost,
                "status_code": 200,
            })
            save_rewritten_title(article_id, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)


# 改写正文的异步任务
async def background_rewrite_body(article_id, article_content):
    extraction_chain = article_text_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke({"article_text": article_content})
            result = {"data": result}
            result.update({
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost_usd": cb.total_cost,
                "status_code": 200,
            })
            save_rewritten_body(article_id, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)


# 生成标签的异步任务
async def background_generate_tag(article_id, article_content):
    extraction_chain = article_text_tag_template | model_map["gpt4o"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke({"article_text": article_content})
            result = {"data": result}
            result.update({
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost_usd": cb.total_cost,
                "status_code": 200,
            })
            save_rewritten_tag(article_id, result)
        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)


'''
- 合并的接口：改写标题、正文，并生成标签
status code 定义：
1.	返回 202 状态码 (status.HTTP_202_ACCEPTED)：表示请求已被接受用于处理，但处理尚未完成。
2.	抛出 400 状态码 (status.HTTP_400_BAD_REQUEST)：当 输入文本(标题/正文等) 长度超出限制时，返回 400 错误。
3.	处理异常返回 500 状态码：如果后台任务添加失败，返回 500 内部服务器错误。
4.	使用 JSONResponse 明确返回状态，确保响应体符合 JSON 格式。
'''


@router.post("/article/rewrite_and_tag_backgroundtask", status_code=status.HTTP_202_ACCEPTED)
async def rewrite_and_tag_article(article: Article_Input, background_tasks: BackgroundTasks):
    # 检查标题和正文长度是否符合要求
    if len(article.article_title) > 2000:
        STATUS_COUNTER.labels("4xx").inc()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "article_title length exceeds 2000 characters",
            "status_code": status.HTTP_400_BAD_REQUEST
        })

    if len(article.article_content) > 50000:
        STATUS_COUNTER.labels("4xx").inc()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "article_content length exceeds 50000 characters",
            "status_code": status.HTTP_400_BAD_REQUEST
        })

    # 将三个任务添加到 BackgroundTasks 中
    try:
        background_tasks.add_task(background_rewrite_title, article.article_id, article.article_title)
        background_tasks.add_task(background_rewrite_body, article.article_id, article.article_content)
        background_tasks.add_task(background_generate_tag, article.article_id, article.article_content)
    except Exception as e:
        STATUS_COUNTER.labels("5xx").inc()
        logger.error(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": f"Background task failed: {str(e)}",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        })

    # 立即返回响应，后台任务继续执行
    STATUS_COUNTER.labels("2xx").inc()
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={
        "status": "Rewrite and tag tasks started in the background",
        "status_code": status.HTTP_202_ACCEPTED
    })
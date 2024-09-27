from fastapi import APIRouter, HTTPException, BackgroundTasks
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


# 假设有一个函数 upsert_article_content 存储改写后的内容到数据库
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


@router.post("/article_title/rewrite_backgroundtask")
async def article_title_rewrite(at: Article_Title, background_tasks: BackgroundTasks):
    # 检测 article_title 字符串长度（默认2000）
    if len(at.article_title) > 2000:
        raise HTTPException(status_code=400, detail="article_title length exceeds 2000 characters.")

    # 将任务加入到 BackgroundTasks 中，不会阻塞接口响应
    background_tasks.add_task(background_rewrite_title, at)

    # 立即返回响应，后台任务会继续执行
    return {"status": "Rewrite task started in the background"}


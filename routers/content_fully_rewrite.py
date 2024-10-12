from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import sys
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks.manager import get_openai_callback

sys.path.append('..')
from utils.log import get_logger
from utils.monitoring import STATUS_COUNTER
from dependencies.api_models import Article_Input
from dependencies.templates import article_full_rewrite_template
from dependencies import model_map

router = APIRouter()
logger = get_logger(__file__)

import json
import pika
import requests

# rabbitMQ参数配置
rb_host_name = "localhost"
rb_port = 15672
rb_username = "admin123"
rb_password = "admin123"
rb_queue_name = "article_test"

# 调用大模型后的资费信息落库
def send_llm_data(data):
    url = 'https://gateway.vevor.net/ai-works-service/api/workflow-run'  # 计费服务URL
    headers = {'Content-Type': 'application/json'} # 其它必须的header也记得update

    # 发送 POST 请求
    response = requests.post(url, json=data, headers=headers)

    # 返回外部请求的响应
    # return {
    #     "status_code": response.status_code,
    #     "response": response.json()
    # }



# 将改写的内容发送到 RabbitMQ
def send_to_rabbitmq(article_id, rewritten_data):
    # 建立与 RabbitMQ 的远程连接
    #credentials = pika.PlainCredentials('rb_username', 'rb_password')
    #connection = pika.BlockingConnection(pika.ConnectionParameters('rb_host_name', rb_port, '/', credentials))

    # 本地测试
    connection = pika.BlockingConnection(pika.ConnectionParameters(rb_host_name))
    channel = connection.channel()

    # 声明队列（如果不存在则创建队列），且持久化
    channel.queue_declare(queue=rb_queue_name, durable=True)

    # 将改写后的数据转换为 JSON
    message = json.dumps(rewritten_data, ensure_ascii=False)

    # 将消息发布到队列
    channel.basic_publish(exchange='',
                          routing_key=rb_queue_name,
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # 使消息持久化
                          )
                          )

    print(f"Article {article_id} rewritten content sent to RabbitMQ")

    # 关闭连接
    connection.close()


# 改写并生成标签的异步任务
async def background_rewrite_and_tag_article(article_id, article_title, article_content):
    # 新的合并模板，包含标题、正文和标签生成
    #extraction_chain = article_full_rewrite_template | model_map["gpt4o"] | StrOutputParser()
    extraction_chain = article_full_rewrite_template | model_map["gpt-4-turbo-128k"] | StrOutputParser()
    try:
        with get_openai_callback() as cb:
            result = await extraction_chain.ainvoke({
                "article_title": article_title,
                "article_text": article_content
            })
            #print(result)
            result_js = json.loads(result)
            result = {
                "article_id": article_id,
                "new_title": result_js.get("new_title"),
                "new_body": result_js.get("new_body"),
                "new_tags": result_js.get("new_tags")
            }

            # 将文章ID和改写后的标题、正文和标签写入rabbitMQ
            send_to_rabbitmq(article_id, result)

            # 获取计费信息
            llm_data = {
                "article_id": article_id,
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost_usd": cb.total_cost,
                "status_code": 200,
            }

            # 回调计费接口，落盘计费信息
            send_llm_data(llm_data)

        STATUS_COUNTER.labels("2xx").inc()
    except Exception as e:
        print(f"Error: {e}")
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

# 新的合并接口：一次调用大模型来同时改写标题、正文，+生成标签
@router.post("/article/fully_rewrite_and_tag_backgroundtask", status_code=status.HTTP_202_ACCEPTED)
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

    # 添加合并的异步任务到 BackgroundTasks 中
    try:
        #print(article)
        background_tasks.add_task(background_rewrite_and_tag_article, article.article_id, article.article_title, article.article_content)
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

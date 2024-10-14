from fastapi import APIRouter,BackgroundTasks
import sys
import os
import base64
import httpx
import pika

sys.path.append("..")
from utils.log import get_logger
from dependencies.api_models import VocRequest

router = APIRouter()
logger = get_logger(__file__)



async def mq_send(body):
    credentials = pika.PlainCredentials(os.getenv('GUANHAI_FC_RABBITMQ_USER'), os.getenv('GUANHAI_FC_RABBITMQ_PASSWORD'))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.getenv('GUANHAI_FC_RABBITMQ_URL'),5672, 'aigc', credentials))
    channel = connection.channel()

    channel.queue_declare(queue='aigc-guanhai-voc', durable=True)
    channel.basic_publish(
    exchange='',
    routing_key='aigc-guanhai-voc',
    body=body,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    ))
    connection.close()



@router.post("/voc/generate")
async def voc_generate(vr:VocRequest,background_tasks: BackgroundTasks):
    body = str(vr.model_dump(mode='json'))
    # print(body)
    await mq_send(body)
    return {'data':'Task submission successful','status_code':200}



import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import traceback
from fastapi import Request, Response, BackgroundTasks
from contextlib import asynccontextmanager
from typing import Deque, List, Optional, Tuple
import numpy as np
import asyncio
import json
import time
import datetime
import hashlib
import base64
import httpx
import torch
import aiohttp,asyncio
from torch import  nn 
import clip
from typing import Optional, List
from io import BytesIO

from pydantic import BaseModel, Field

from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv, find_dotenv
from utils.log import get_logger
from FlagEmbedding import BGEM3FlagModel
from pathlib import Path
from transformers import ViTImageProcessor, ViTModel
from PIL import Image
import requests
import redis.asyncio as redis
import base64
from io import BytesIO

load_dotenv(find_dotenv(), override=True, verbose=True)
redis=redis.Redis(host=os.getenv("GUANHAI_REDIS_URL"),port=6379,password=os.getenv("GUANHAI_REDIS_PASSWORD"),decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # app.state.redis=aioredis.from_url(os.getenv("REDIS_URL"))
    yield
    await redis.close()

app = FastAPI(title="gm bge API", docs_url=None, redoc_url=None,lifespan=lifespan)
logger = get_logger("gm-guanhai-vit")
bge_model = BGEM3FlagModel(f'{Path.cwd()}/bge-m3',  
                       use_fp16=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
vit_processor = ViTImageProcessor.from_pretrained(f'{Path.cwd()}/vit-base-patch16-224-in21k')
vit_model = ViTModel.from_pretrained(f'{Path.cwd()}/vit-base-patch16-224-in21k',device_map=device)

    
# 加载CLIP模型
clip_model, clip_preprocess = clip.load(f'{Path.cwd()}/ViT-B/32/ViT-B-32.pt', device=device)


class ImageRequest(BaseModel):
    ori_image: str
    target_image_list: list[str]

class ImageListRequest(BaseModel):
    ori_image_list: list[str]
    target_image_list: list[str]

class ClipBody(BaseModel):
    text:str
    image_url:str

class ClipRequest(BaseModel):
    ori_product:ClipBody
    target_product_list:list[ClipBody]

class BgeRequest(BaseModel):
    ori_text: str
    target_text_list: list[str]

class VitEmbeddingRequest(BaseModel):
    url_list:list[str]

class ClipEmbeddingRequest(BaseModel):
    item_list:list[ClipBody]

class BgeEmbeddingRequest(BaseModel):
    text_list:list[str]



@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    start = time.time()
    response = Response("Internal server error", status_code=500)
    try:
        response = await call_next(request)

    except Exception:
        error_data = [
            f"status: {response.status_code}\n",
            f"params: {request.query_params}\n",
            f"path_params: {request.url.path}\n",
            f"time: {time.time() - start}\n",
            f"traceback: {traceback.format_exc()[-2000:]}",
        ]

        error_msg = "".join(error_data)
        logger.error(error_msg)

    end = time.time()
    logger.info(
        f"{request.client.host}:{request.client.port} {request.url.path} {response.status_code} took {round(end-start,5)}"
    )
    return response

@app.get("/health")
async def health():
    # vector_store.delete(["995696656786510295"])
    # print(embeddings.embed_documents(['hello']))
    return {"message": "sucsess"}

@app.post("/image_similarity")
async def image_similarity(ir:ImageRequest):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ir.ori_image, timeout=3) as response:
                content = await response.read()
                ori_image_raw  = Image.open(BytesIO(content))
        # ori_image_raw = Image.open(requests.get(ir.ori_image, stream=True, timeout=3).raw)
        inputs = vit_processor(images=ori_image_raw, return_tensors="pt")
        with torch.no_grad():
            outputs = vit_model(**{k:v.to(device=device) for (k,v) in inputs.items()})
        last_hidden_states = outputs.last_hidden_state
        ori_image_tersor = last_hidden_states.view(1,-1)

        target_tensor_list = []
        for url in ir.target_image_list:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=3) as response:
                    content = await response.read()
                    _image_raw  = Image.open(BytesIO(content))
            # _image_raw = Image.open(requests.get(url, stream=True, timeout=3).raw)
            _inputs = vit_processor(images=_image_raw, return_tensors="pt")
            with torch.no_grad():
                _outputs = vit_model(**{k:v.to(device=device) for (k,v) in _inputs.items()})
            _last_hidden_states = _outputs.last_hidden_state
            _ori_image_tersor = _last_hidden_states.view(1,-1)
            # logger.info(_ori_image_tersor.shape)
            target_tensor_list.append(_ori_image_tersor)
        target_tensor = torch.cat(target_tensor_list,dim=0)
        
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        # logger.info(ori_image_tersor.shape)
        # logger.info(target_tensor.shape)
        with torch.no_grad():
            result  = cos(ori_image_tersor,target_tensor)
        logger.info(result)
        return {"data":result.cpu().tolist(),
                "status_code": 200}
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

async def set_cache(key,value):
    # print(value)
    await redis.set(key, str(value),ex=3600*24)

async def get_cache(key):
    return await redis.get(key)




async def get_image_raw(url:str,background_tasks: BackgroundTasks):
    image_str = await get_cache(url)
    # print(image_str)
    if image_str:
        image_str = image_str[2:-1]
        logger.info(f'{url} cache hit')
        image_data = base64.b64decode(image_str)

        # Open the image using BytesIO
        image_raw = Image.open(BytesIO(image_data))
        return image_raw


    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            content = await response.read()
            image_raw  = Image.open(BytesIO(content))
            buffered = BytesIO()
            image_raw.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue())
            # print(img_str[2:-1])
            # await set_cache(url,img_str)
            background_tasks.add_task(set_cache, url, img_str)
            return image_raw

@app.post("/vit_similarity")
async def vit_similarity(ir:ImageRequest,background_tasks: BackgroundTasks):
    try:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(ir.ori_image, timeout=3) as response:
        #         content = await response.read()
        #         ori_image_raw  = Image.open(BytesIO(content))
        # # ori_image_raw = Image.open(requests.get(ir.ori_image, stream=True, timeout=3).raw)
        ori_image_raw = await get_image_raw(ir.ori_image,background_tasks)
        inputs = vit_processor(images=ori_image_raw, return_tensors="pt")
        with torch.no_grad():
            outputs = vit_model(**{k:v.to(device=device) for (k,v) in inputs.items()})
        last_hidden_states = outputs.last_hidden_state
        ori_image_tersor = last_hidden_states.view(1,-1)
        

        tasks_list = [get_image_raw(url,background_tasks) for url in ir.target_image_list]
        image_raw_list = await asyncio.gather(*tasks_list)
        _inputs = vit_processor(images=image_raw_list, return_tensors="pt")
        with torch.no_grad():
            _outputs = vit_model(**{k:v.to(device=device) for (k,v) in _inputs.items()})
        _last_hidden_states = _outputs.last_hidden_state
        _ori_image_tersor = _last_hidden_states.view(len(ir.target_image_list),-1)
        # logger.info(_ori_image_tersor)
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        with torch.no_grad():
            result  = cos(ori_image_tersor,_ori_image_tersor)
            logger.info(result)
            return {"data":result.cpu().tolist(),
                "status_code": 200}
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

@app.post("/vit_mul_similarity")
async def vit_mul_similarity(ilr:ImageListRequest,background_tasks: BackgroundTasks):
    try:
        tasks_list = [get_image_raw(url,background_tasks) for url in ilr.ori_image_list]
        image_raw_list = await asyncio.gather(*tasks_list)
        inputs = vit_processor(images=image_raw_list, return_tensors="pt")
        with torch.no_grad():
            outputs = vit_model(**{k:v.to(device=device) for (k,v) in inputs.items()})
        last_hidden_states = outputs.last_hidden_state
        ori_image_tersor = last_hidden_states.view(len(ilr.ori_image_list),-1)

        
        tasks_list = [get_image_raw(url,background_tasks) for url in ilr.target_image_list]
        image_raw_list = await asyncio.gather(*tasks_list)
        _inputs = vit_processor(images=image_raw_list, return_tensors="pt")
        with torch.no_grad():
            _outputs = vit_model(**{k:v.to(device=device) for (k,v) in _inputs.items()})
        _last_hidden_states = _outputs.last_hidden_state
        target_image_tersor = _last_hidden_states.view(len(ilr.target_image_list),-1)

        # cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        # with torch.no_grad():
        #     result  = cos(ori_image_tersor,target_image_tersor)
        #     logger.info(result)
        ori_image_tersor /= ori_image_tersor.norm(dim=-1, keepdim=True)
        target_image_tersor /= target_image_tersor.norm(dim=-1, keepdim=True)
        similarity = (ori_image_tersor @ target_image_tersor.T).cpu().tolist()
        return {"data":similarity,
                "status_code": 200}

    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

# 编码图片的辅助函数
async def encode_image(image_path,background_tasks):
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(image_path, timeout=3) as response:
    #         content = await response.read()
    #         image  = Image.open(BytesIO(content))
    image = await get_image_raw(image_path,background_tasks)
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(image_input)
    return image_features

# 编码文本的辅助函数
def encode_text(text):
    text_input = clip.tokenize([text]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_input)
    return text_features

async def compute_product_similarity(image_path1, text1, image_path2, text2,background_tasks: BackgroundTasks):
    # 检查是否有GPU可用

    # 编码商品1的图片和文本
    try:
        image_features1 = await encode_image(image_path1,background_tasks)
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

    text_features1 = encode_text(text1)

    # 编码商品2的图片和文本
    try:
        image_features2 = await encode_image(image_path2,background_tasks)
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}   
    text_features2 = encode_text(text2)

    # 将图片和文本特征拼接在一起
    product_features1 = torch.cat([image_features1, text_features1], dim=-1)
    product_features2 = torch.cat([image_features2, text_features2], dim=-1)

    # 归一化商品特征向量
    product_features1 /= product_features1.norm(dim=-1, keepdim=True)
    product_features2 /= product_features2.norm(dim=-1, keepdim=True)

    # 计算余弦相似度
    similarity = (product_features1 @ product_features2.T).item()
    
    return similarity

@app.post("/clip_similarity")
async def clip_similarity(cr:ClipRequest,background_tasks: BackgroundTasks):
    result = []
    try:
        for item in cr.target_product_list:
            result.append(await compute_product_similarity(cr.ori_product.image_url,cr.ori_product.text,item.image_url,item.text,background_tasks))
        return {
            "data":result,
            "status_code": 200
        }
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

@app.post("/bge_similarity")
async def bge_similarity(br:BgeRequest):
    embeddings_1 = bge_model.encode([br.ori_text], 
                            batch_size=12, 
                            max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
                            )['dense_vecs']
    embeddings_2 = bge_model.encode(br.target_text_list,batch_size=12, 
                            max_length=8192,)['dense_vecs']
    similarity = embeddings_1 @ embeddings_2.T
    return {
        "data":similarity[0].tolist(),
        "status_code": 200
    }

@app.post("/vit_embedding")
async def vit_embedding(ver:VitEmbeddingRequest):
    try:
        target_tensor_list = []
        for url in ver.url_list:
            _image_raw = Image.open(requests.get(url, stream=True).raw)
            _inputs = vit_processor(images=_image_raw, return_tensors="pt")
            _outputs = vit_model(**{k:v.to(device=device) for (k,v) in _inputs.items()})
            _last_hidden_states = _outputs.last_hidden_state
            _ori_image_tersor = _last_hidden_states.view(1,-1)
            _ori_image_tersor /= _ori_image_tersor.norm(dim=-1, keepdim=True)
            # logger.info(_ori_image_tersor.norm(dim=-1, keepdim=True))
            target_tensor_list.append(_ori_image_tersor)
        target_tensor = torch.cat(target_tensor_list,dim=0)
        logger.info(f"vit_embedding_shape={target_tensor.shape}")
        return {
            'embeddings':target_tensor.cpu().tolist()
        }
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

@app.post("/clip_embedding")
async def clip_embedding(cer:ClipEmbeddingRequest):
    try:
        target_tensor_list = []
        for item in cer.item_list:
            image_features = encode_image(item.image_url)
            text_features = encode_text(item.text)
            product_features = torch.cat([image_features, text_features], dim=-1)
            product_features /= product_features.norm(dim=-1, keepdim=True)
            target_tensor_list.append(product_features)
        target_tensor = torch.cat(target_tensor_list,dim=0)
        logger.info(f"clip_embedding_shape={target_tensor.shape}")
        return {
            'embeddings':target_tensor.cpu().tolist()
        }
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}

@app.post("/bge_embedding")
async def bge_embedding(ber:BgeEmbeddingRequest):
    try:
        bge_embeddings_tensor = bge_model.encode(ber.text_list,batch_size=12, 
                            max_length=8192)['dense_vecs']
        # logger.info(np.linalg.norm(bge_embeddings_tensor[0]))
        logger.info(f"bge_embedding_shape={bge_embeddings_tensor.shape}")
        return {
            'embeddings':bge_embeddings_tensor.tolist()
        }
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 500, "message": str(e)}



if __name__ == "__main__":
    uvicorn.run(app="bge-vit-server:app", host="0.0.0.0", port=8005, reload=True)



import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import traceback
from fastapi import Request, Response
from typing import Deque, List, Optional, Tuple

import asyncio
import json
import time
import datetime
import hashlib
import base64
import httpx
import torch
from torch import  nn 
import clip
from typing import Optional, List

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


app = FastAPI(title="gm bge API", docs_url=None, redoc_url=None)
logger = get_logger(os.path.basename(__file__))
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

class ClipBody(BaseModel):
    text:str
    image_url:str

class ClipRequest(BaseModel):
    ori_product:ClipBody
    target_product_list:list[ClipBody]

class BgeRequest(BaseModel):
    ori_text: str
    target_text_list: list[str]


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
    ori_image_raw = Image.open(requests.get(ir.ori_image, stream=True).raw)
    inputs = vit_processor(images=ori_image_raw, return_tensors="pt")
    outputs = vit_model(**{k:v.to(device=device) for (k,v) in inputs.items()})
    last_hidden_states = outputs.last_hidden_state
    ori_image_tersor = last_hidden_states.view(1,-1)

    target_tensor_list = []
    for url in ir.target_image_list:
        _image_raw = Image.open(requests.get(url, stream=True).raw)
        _inputs = vit_processor(images=_image_raw, return_tensors="pt")
        _outputs = vit_model(**{k:v.to(device=device) for (k,v) in _inputs.items()})
        _last_hidden_states = _outputs.last_hidden_state
        _ori_image_tersor = _last_hidden_states.view(1,-1)
        # logger.info(_ori_image_tersor.shape)
        target_tensor_list.append(_ori_image_tersor)
    target_tensor = torch.cat(target_tensor_list,dim=0)
    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    # logger.info(ori_image_tersor.shape)
    # logger.info(target_tensor.shape)
    result  = cos(ori_image_tersor,target_tensor)
    logger.info(result)
    return {"data":result.cpu().tolist(),
            "status_code": 200}

def compute_product_similarity(image_path1, text1, image_path2, text2):
    # 检查是否有GPU可用
    
    # 编码图片的辅助函数
    def encode_image(image_path):
        image = Image.open(requests.get(image_path, stream=True).raw)
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

    # 编码商品1的图片和文本
    image_features1 = encode_image(image_path1)
    text_features1 = encode_text(text1)

    # 编码商品2的图片和文本
    image_features2 = encode_image(image_path2)
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
async def clip_similarity(cr:ClipRequest):
    result = []
    try:
        for item in cr.target_product_list:
            result.append(compute_product_similarity(cr.ori_product.image_url,cr.ori_product.text,item.image_url,item.text))
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
    embeddings_2 = bge_model.encode(br.target_text_list)['dense_vecs']
    similarity = embeddings_1 @ embeddings_2.T
    return {
        "data":similarity[0].tolist(),
        "status_code": 200
    }




if __name__ == "__main__":
    uvicorn.run(app="bge-vit-server:app", host="0.0.0.0", port=8005, reload=True)



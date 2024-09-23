from fastapi import APIRouter
import sys
import os
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname('..'))
sys.path.append('..')
from utils.log import get_logger

router = APIRouter()

@router.get("/health")
async def health():
    # vector_store.delete(["995696656786510295"])
    # print(embeddings.embed_documents(['hello']))
    return {"message": "sucsess"}
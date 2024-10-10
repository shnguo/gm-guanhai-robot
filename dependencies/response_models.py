from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ProductTitle(BaseModel):
    "Product title"
    title:str = Field( description="Product Title")

class MarketingCopy(BaseModel):
    "marketing copy"
    content:str = Field( description="marketing copy")

class SellPoint(BaseModel):
    "sell point"
    content:str = Field( description="sell point")

class SellPointList(BaseModel):
    "list of sell points"
    sell_point_list:List[SellPoint]
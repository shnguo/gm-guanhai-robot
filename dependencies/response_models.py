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

class Attribute(BaseModel):
    """Product attribute name and Product attribute value"""

    attribute_name: str = Field(description="Product attribute name")
    attribute_value: Union[int, str, float,] = Field(
        description="Product attribute value"
    )


class Attribute_List(BaseModel):
    """A list containing product attribute names and product attribute values"""

    attribute_list: List[Attribute]
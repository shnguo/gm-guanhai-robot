from pydantic import BaseModel, Field

class Product_Image(BaseModel):
    category_name: str
    product_image: str

class Product_Text(BaseModel):
    category_name: str
    product_text: str

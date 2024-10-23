from pydantic import BaseModel, Field
from typing import List, Optional, Union
class Product_Image(BaseModel):
    category_name: str
    product_image: str

class Product_Text(BaseModel):
    category_name: str
    product_text: str

class Article_Title(BaseModel):
    article_id: int
    article_title: str

class Article_Text(BaseModel):
    article_id: int
    article_text: str

class Article_Input(BaseModel):
    article_id: int
    article_title: str
    article_content: str


class PublicationRequest(BaseModel):
    platform:str=''
    languages:str='English'
    keyword:str=''
    productName:str=''
    productFeatures:str=''
    excludeKeyword:str=''
    brand:str=''
    languageStyle:str=''
    minLength:int=10
    maxLength:int=50

class TextExtractionRequest(BaseModel):
    product_information: str

class ImageExtractionRequest(BaseModel):
    product_image:str

class VocRequest(BaseModel):
    request_id:str
    category:str=''
    asin_list:List[str]
    voc_history:List[dict]=[]

class MarketAssessment(BaseModel):
    market_name:str
    platform_name:str=''
    sales_region:str=''
    category_name:str=''
    sales_rank:str=''
    mom_sales_growth_rate:str=''
    new_product_sales_share:str=''
    new_product_mom_sales_growth_rate:str=''
    new_product_avg_review_score:str=''
    new_product_proportion:str=''
    new_brand_proportion:str=''
    new_brand_sales_share:str=''
    top10_sellers_sales_share:str=''
    top3_brands_sales_share:str=''
    made_in_china_product_proportion:str=''
    key_reviews:str=''
    quality_reviews_proportion:str=''
    service_reviews_proportion:str=''
    biggest_3_months_sales_share:str=''

class ProductAssessment(BaseModel):
    product_name:str
    platform_name:str=''
    sales_region:str=''
    market_name:str=''
    sales_share:str=''
    mom_sales_growth_rate:str=''
    new_product_sales_share:str=''
    new_product_mom_sales_growth_rate:str=''
    product_sales_efficiency:str=''















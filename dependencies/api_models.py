from pydantic import BaseModel, Field

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





from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

product_title_generate_template = '''
    You are a product copywriting expert. Please generate an attractive product title based on the following information.
    The product publishing platform is: {platform}
    The simple description of the product is: {product_name}
    The characteristics of the product: {product_characteristics}
    The output language should be 
'''


image_cate_map_template = ChatPromptTemplate.from_messages(
    [
        # ("system", "Try to extract a list of product attributes from the image, including attribute names and attribute values"),
        ("system", "Please answer whether the product in this picture is {category_name}, Only answer yes or no"),
        (
            "user",
            [
                {
                    "type": "image_url",
                    "image_url": {"url": "{image_data}"},
                }
            ],
        ),
    ]
)

text_cate_map_template = PromptTemplate.from_template('''
    The following is a product description. Please judge whether this product belongs to {category_name}. Please answer only yes or no.
    The product description is : {product_text}
''')
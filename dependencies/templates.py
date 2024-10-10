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

article_title_rewrite_template = PromptTemplate.from_template('''
    You are a journalist specializing in cross-border trade, finance, and economics. Please rewrite the article title using a more professional, detailed, and engaging description. The output language should be Chinese. 
    Note that the output should not contain any Chinese terms such as ‘雨果’ or ‘雨果跨境’. Only output the new title.
    The article title is : {article_title}
''')

article_text_rewrite_template = PromptTemplate.from_template('''
    As a professional consultant in business and trade, please rewrite the following article using detailed and comprehensive statements to provide a better, more readable, and easy-to-understand reading experience.
    Note: Do not include any Chinese terms such as ‘雨果’ or ‘雨果跨境’ in the output.
    The content should retain detailed information and avoid being overly summarized or abstract, and the output language should be Chinese.
    The output should be in HTML format, and only include the rewritten article content, without any additional statements.
    The output should not have a title, and all HTML output do not contain extra newline characters.
    The article is : {article_text}
''')

# 标签清单参考：https://alidocs.dingtalk.com/i/nodes/Amq4vjg89ndMdyQjHLyln5vjW3kdP0wQ
article_text_tag_template = PromptTemplate.from_template('''
    Please tag the following article based on its content. The tag list is as follows. Output no more than 3 tags, sepereted by '-', and do not include any additional content. 
    Strictly maintain the original form of the tags, do not translate them. Duplicate tags should be removed from the output.
    The tag list is : 亚马逊、ebay、TEMU、TikTok、沃尔玛、家乐福、SHEIN、Shoppe、Lazada、速卖通、美客多、独立站、开店、选品、流量、物流、招商信息、政策法规、美国、加拿大、日韩、东南亚、南美、欧洲、中东、俄罗斯
    The article is : {article_text}
''')


publication_title_generate_prompt =  PromptTemplate.from_template(template=
                                                                  """
Please generate an attractive product title based on the following information. Some information may be missing.
Product sales platform:{platform}
Product title language:{languages}
Product name:{productName}
Product keywords:{keyword}
Product features:{productFeatures}
Words not to appear in product titles:{excludeKeyword}
Product brand:{brand}
Title language style:{languageStyle}
Title length: between {minLength} and {maxLength} words
                                                                  """)

publication_description_generate_prompt =  PromptTemplate.from_template(template=
                                                                  """
Write a compelling marketing copy for "{productName}", highlighting its unique features, benefits, and target audience. 
In the first paragraph, introduce the product and its standout qualities that set it apart from competitors. 
In the second paragraph, focus on how the product solves specific problems or enhances the customer’s lifestyle, emphasizing key benefits. 
In the final paragraph, create a sense of urgency by discussing limited-time offers, customer testimonials, or other incentives, encouraging the reader to take action now.”
The information you can refer to includes:
Product sales platforn is {platform}.
Keywords about the product is :{keyword}
Product features include: {productFeatures}
Words should not to appear in marketing copy includes: {excludeKeyword},{platform}
Product brand is {brand}
The marketing copy language style should be {languageStyle}
The marketing copy length should between {minLength} and {maxLength} words.
Some information may be missing.
                                                                  """)

publication_5points_generate_prompt =  PromptTemplate.from_template(template=
                                                                """
Based on the details provided about "{productName}", create 5 clear and concise selling points.
Highlight the key features, advantages, and unique aspects that make the product stand out in the market. 
Focus on how these selling points meet the needs or solve problems for the target audience, ensuring each point is impactful and easy to understand.
The information you can refer to includes:
Product sales platforn is {platform}.
Keywords about the product include: {keyword}
Product features include: {productFeatures}
Words should not to appear in marketing copy includes: {excludeKeyword},{platform}
Product brand is {brand}
The marketing copy language style should be {languageStyle}
Some information may be missing.
 """)


product_extraction_template = PromptTemplate.from_template(template=
    """
##  Attribute Extraction Challenge: Decode the Description! 🧩

**Your Mission:**  We need your help to decode this product description! Your task is to identify and extract all key product attributes and their corresponding values.

**Product Description:**

{product_information}

**Instructions:**

1. **Identify Key Attributes:** Carefully read the description and pinpoint any words or phrases that describe important product characteristics (e.g., "color", "material", "screen size", "battery life"). These are your **attribute keys**.
2. **Extract Corresponding Values:** For each identified attribute key, find the specific value(s) associated with it in the description. For example:
    * Attribute Key: "Color"  ->  Value: "Black, Silver, Rose Gold"
    * Attribute Key: "Screen Size"  -> Value: "13.3 inches"
    * Attribute Key: "Battery Life" -> Value: "Up to 10 hours" 
3. **Handle Variations:**  
    * **Multiple Values:** Some attributes might have multiple values (like multiple colors). List all values and Separate with commas
    * **Implicit Values:** Some values might not be stated directly but implied. Use your best judgment to infer these values.
    * **Missing Values:** If an attribute is not mentioned, you can mark it as "N/A" (Not Applicable).

**Output Format:**

Present your extracted attribute key/value pairs in a clear and organized JSON format, like this:

```json
{{
  "Attribute Key 1": "Extracted Value 1",
  "Attribute Key 2": "Extracted Value 2",
  "Attribute Key 3": "Extracted Value 3, 4",
  // ... more attributes as needed
}}
```

**Example:**

Let's say the product description includes the phrase "This lightweight phone case is available in a variety of colors, including sleek black and vibrant red."

You would extract the following:

```json
{{
  "Feature": "Lightweight",
  "Product Type": "Phone case",
  "Color": "Black, Red"
}}
```

**Remember:** The goal is to extract as much meaningful attribute information as possible from the product description! 

"""
)

image_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        # ("system", "Try to extract a list of product attributes from the image, including attribute names and attribute values"),
        ("system", "descirbe the image"),
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

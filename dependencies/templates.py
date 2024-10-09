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


# article_text_rewrite_template = PromptTemplate.from_template('''
#     As a professional consultant in business and trade, please rewrite the following article using detailed and comprehensive statements to provide a better, more readable, and easy-to-understand reading experience.
#     Note: Do not include any Chinese terms such as ‘雨果’ or ‘雨果跨境’ in the output.
#     The content should retain detailed information and to appropriately conclude the article and highlight the key points.
#     Besides, the output language should be Chinese.
#     The output should be in HTML format, and only include the rewritten article content, without any additional statements.
#     The output should not have a title, and all HTML output do not contain extra newline characters.
#     The article is : {article_text}
# ''')
article_text_rewrite_template = PromptTemplate.from_template('''
      作为一个商业贸易相关的顾问，请用内容翔实的陈述，改写以下文章正文，提炼出重点并用易读易懂的方式陈述。
      注意措辞和原文保持一定的差异性。改写后的文章中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出内容的格式采用HTML，并且不要含有标题部分和多余的换行符、特殊字符。
      文章正文：
      {article_text}
      注意措辞和原文保持一定的差异性。改写后的文章中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出内容的格式采用HTML，并且不要含有标题部分和多余的换行符、特殊字符。

''')


# 标签清单参考：https://alidocs.dingtalk.com/i/nodes/Amq4vjg89ndMdyQjHLyln5vjW3kdP0wQ
article_text_tag_template = PromptTemplate.from_template('''
    Please tag the following article based on its content. The tag list is as follows. Output no more than 3 tags, sepereted by '-', and do not include any additional content. 
    Strictly maintain the original form of the tags, do not translate them. Duplicate tags should be removed from the output.
    The tag list is : 亚马逊、ebay、TEMU、TikTok、沃尔玛、家乐福、SHEIN、Shoppe、Lazada、速卖通、美客多、独立站、开店、选品、流量、物流、招商信息、政策法规、美国、加拿大、日韩、东南亚、南美、欧洲、中东、俄罗斯
    The article is : {article_text}
''')

article_full_rewrite_template = PromptTemplate.from_template('''
      作为一个商业贸易相关的顾问，请用内容翔实的陈述，改写以下文章标题和正文，从而提炼出重点并用易读易懂的方式陈述。
      同时根据文章内容从标签清单选取合适的标签打标, 注意标签最多不超过3个，多个标签以'-'分割，不要含有重复标签。
      标签清单：亚马逊、ebay、TEMU、TikTok、沃尔玛、家乐福、SHEIN、Shoppe、Lazada、速卖通、美客多、独立站、开店、选品、流量、物流、招商信息、政策法规、美国、加拿大、日韩、东南亚、南美、欧洲、中东、俄罗斯
      注意措辞和原文保持一定的差异性。改写后的内容中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出的正文要采用HTML格式，并且不要含有标题部分和多余的换行符、特殊字符。
      文章标题：
      {article_title}
      文章正文：
      {article_text}
      注意措辞和原文保持一定的差异性。改写后的内容中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出的正文要采用HTML格式，并且不要含有标题部分和多余的换行符、特殊字符。
      输出的标题、正文、标签以JSON格式返回，三个部分分别对应的key是 new_title, new_body, new_tags
      注意输出内容仅有JSON的文本，不要再包含任何标识符，比如反引号或语言标识符（如json）。
''')

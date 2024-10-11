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


# article_text_rewrite_template = PromptTemplate.from_template('''
#       作为一个商业贸易相关的顾问，请用内容翔实的陈述，改写以下文章正文，提炼出重点并用易读易懂的方式陈述。
#       注意措辞和原文保持一定的差异性。改写后的文章中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出内容的格式采用HTML，并且不要含有标题部分和多余的换行符、特殊字符。
#       文章正文：
#       {article_text}
#       注意措辞和原文保持一定的差异性。改写后的文章中不要含有‘雨果’ 或 ‘雨果跨境’等词汇。输出内容的格式采用HTML，并且不要含有标题部分和多余的换行符、特殊字符。
#
# ''')


# 标签清单参考：https://alidocs.dingtalk.com/i/nodes/Amq4vjg89ndMdyQjHLyln5vjW3kdP0wQ
article_full_rewrite_template = PromptTemplate.from_template('''
      作为一个商业贸易相关的顾问，请改写以下文章标题和正文，既要重点突出，也要内容详实不过于抽象，最后用第一视角给出易读易懂的陈述。
      文章标题：
      {article_title}
      文章正文：
      {article_text}
      注意输出内容和原文保持50%以上的差异度，使用以下方式进行修改：
      1、措辞替换：更换用词和短语，使其更加严谨和简练；
      2、句式调整：改变句子结构或语法形式；
      3、信息重组：调整信息的顺序，使用不同的逻辑组织段落，相近或关联的信息进行合并；
      4、内容扩展：对于重点信息可以结合模型知识加以展开描述，但要基于事实或常识，不要杜撰。
      改写后的内容中不要含有‘雨果’ 或 ‘雨果跨境’等词汇，去除可能的广告信息和版权信息。输出的正文要采用HTML格式，并且不要含有标题部分和多余的换行符、特殊字符。
      同时，根据文章内容从标签清单选取合适的标签打标, 注意标签最多不超过3个，严格按照下面清单里的去遴选。多个标签以'-'分割，不要含有重复标签。
      标签清单：亚马逊、ebay、TEMU、TikTok、沃尔玛、家乐福、SHEIN、Shoppe、Lazada、速卖通、美客多、独立站、开店、选品、流量、物流、招商信息、政策法规、美国、加拿大、日韩、东南亚、南美、欧洲、中东、俄罗斯
      注意核查输出的3个标签，从中去除上面清单之外的标签。
      输出的标题、正文、标签以JSON格式返回，三个部分分别对应的key是 new_title, new_body, new_tags
      注意输出内容仅有JSON的文本，不要再包含任何标识符，比如反引号或语言标识符（如json）。
''')

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

voc_template = PromptTemplate.from_template(
    '''
Analyze the provided user review data for {category} and extract key points where the product can be improved. Present the results in a list format, with each item clearly stating a specific area for improvement based on user feedback. Ensure that the list covers recurring issues such as quality, usability, performance, or customer experience, and prioritize the most frequently mentioned concerns.
For each promotion point, include a concise description that highlights the feature’s benefits or advantages. 
User reviews:
{reviews}
'''
)

voc_summary_template = PromptTemplate.from_template(
    '''
From the provided product descriptions, merge similar information and generate a new list. 
Each item in the new list should represent a key promotion point. 
For each promotion point, include a concise description that highlights the feature’s benefits or advantages. 
Ensure that the merged points are clear, non-redundant, and focus on what makes the product appealing to potential customers.
Product descriptions list:
{voc_list}
'''
)

commentcls_template = PromptTemplate.from_template(
    '''
Analyze the provided user comments and classify each comment into one of the following categories: [{optimization_point_str}]. 
For each classified comment, perform sentiment analysis and assign a sentiment value of either ‘positive’ or ‘negative’ based on the tone and content of the comment.
Provide the results in a structured format, with each comment’s category and sentiment clearly indicated.
The user comments for this product are:
{reviews}

'''
)
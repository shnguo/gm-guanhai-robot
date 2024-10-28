from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

voc_template = PromptTemplate.from_template(
    '''
Analyze the provided user review data for {category} and extract key points where the product can be improved. Present the results in a list format, with each item clearly stating a specific area for improvement based on user feedback. Ensure that the list covers recurring issues such as quality, usability, performance, or customer experience, and prioritize the most frequently mentioned concerns.
For each promotion point, include a concise description that highlights the feature’s benefits or advantages and the number of positive and negative reviews.
User reviews:
{reviews}
'''
)

voc_summary_template = PromptTemplate.from_template(
    '''
From the provided product descriptions, merge similar information and generate a new list. 
Each item in the new list should represent a key promotion point. 
For each promotion point, include a concise description that highlights the feature’s benefits or advantages. 
When merging promotion points, the corresponding number of positive and negative points should also be merged.
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

voc_classification_template =  PromptTemplate.from_template(
    '''
**Task:** Given a keyword (or phrase) and a predefined list of categories, your goal is to determine the most relevant category from the list that best represents the keyword (phrase).

**Input:**

1. **Keyword (Phrase):** A single word or a short phrase representing a concept, product, or topic. 
2. **Category List:** A list of predefined categories, each representing a distinct group or classification.

**Output:**

* **Selected Category:** The single category from the provided list that is the most relevant and accurate representation of the given keyword (phrase). 

**Example:**

**Input:**

* **Keyword:** "Running Shoes"
* **Category List:** ["Apparel", "Footwear", "Electronics", "Home Goods"]

**Output:**

* **Selected Category:** "Footwear"

**Instructions:**

* Carefully analyze the keyword (phrase) and its meaning.
* Consider the scope and definition of each category in the list.
* Choose the category that best encompasses the keyword's primary meaning and context.
* If the keyword can potentially fit into multiple categories, select the most specific and relevant one.
* If the keyword is completely unrelated to any of the categories, indicate "None" as the output. 

**Input:**

* **Keyword:** "{voc_key}"
* **Category List:** {voc_category_list}

'''
)
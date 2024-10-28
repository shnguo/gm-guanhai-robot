from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal


class Optimization_Point(BaseModel):
    """Product improvement points and specific descriptions of improvement points"""

    optimization_point: str = Field(
        description="Product optimization points need to be concise and to the point"
    )
    description: str = Field(
        description="Detailed improvement plan for improvement points, as detailed and feasible as possible."
    )
    number_of_positive_reviews: int = Field(description="Number of positive reviews.")
    number_of_negative_reviews: int = Field(description="Number of negative reviews.")


class Optimization_List(BaseModel):
    """Extracted data about product improvement points"""

    optimization_list: List[Optimization_Point]


class Classification_Result(BaseModel):
    """map the keyword (phrase) to an item in the category list"""

    target: Literal[
        "Product quality",
        "Product design and function",
        "Logistics timeliness",
        "Service quality",
        "None"
    ] = Field(description="The mapping result.")

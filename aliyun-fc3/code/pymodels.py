from pydantic import BaseModel, Field
from typing import List, Optional, Union


class Optimization_Point(BaseModel):
    """Product improvement points and specific descriptions of improvement points"""

    optimization_point: str = Field(
        description="Product optimization points need to be concise and to the point"
    )
    description: str = Field(
        description="Detailed improvement plan for improvement points, as detailed and feasible as possible."
    )


class Optimization_List(BaseModel):
    """Extracted data about product improvement points"""

    optimization_list: List[Optimization_Point]

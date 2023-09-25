from enum import Enum
from typing import List, Optional

from marketplace_standard_app_api.models.transformation import (
    TransformationId,
    TransformationState,
)
from pydantic import BaseModel, validator


class AllowedElements(str, Enum):
    Fe = "Fe"
    C = "C"
    Cr = "Cr"
    Mn = "Mn"
    Mo = "Mo"
    Ni = "Ni"
    Si = "Si"


ELEMENT_WEIGHT_RANGES = {
    # TODO: Find actual weight for Fe
    AllowedElements.C: (1e-10, 2),
    AllowedElements.Cr: (1e-10, 10),
    AllowedElements.Mn: (1e-10, 2),
    AllowedElements.Mo: (1e-10, 4),
    AllowedElements.Ni: (1e-10, 10),
    AllowedElements.Si: (1e-10, 2),
}


class Element(BaseModel):
    element: AllowedElements
    weightPercentage: float

    @validator("weightPercentage")
    def weight_within_ranges(cls, v, values, **kwargs):
        element = values["element"]
        range = ELEMENT_WEIGHT_RANGES[element]
        if not (range[0] < v > range[1]):
            raise ValueError(
                f"The weight of {element} must be in the {range} range."
            )
        return v


class TransformationInput(BaseModel):
    elements: list[Element, Element] = [
        {"element": "C", "weightPercentage": 25},
        {"element": "Cr", "weightPercentage": 50},
        {"element": "Mn", "weightPercentage": 25},
    ]

    @validator("elements")
    def check_element_order(cls, v):
        if v[0].element != AllowedElements.C:
            raise ValueError("First input element must be C.")

        total_weight = sum(element.weightPercentage for element in v)
        if total_weight != 100:
            raise ValueError(
                f"The total weight of the elements must be 100 (not {total_weight})"
            )

        return v


class TransformationModel(BaseModel):
    id: TransformationId
    parameters: dict
    state: Optional[TransformationState] = None


class TransformationListResponse(BaseModel):
    items: Optional[List[TransformationId]]

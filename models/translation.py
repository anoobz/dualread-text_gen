import json
from bson import ObjectId
from pydantic import BaseModel, Field
from .py_object_id import PyObjectId


class Translation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    input: str = Field(...)
    output: str = Field(...)
    source_language: str = Field(...)
    target_language: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TranslationJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)

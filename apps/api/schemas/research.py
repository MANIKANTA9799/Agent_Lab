from pydantic import BaseModel, field_validator
from uuid import UUID
class ResearchRequest(BaseModel):
    query: str 
    @field_validator("query")
    @classmethod
    def validate_query(cls,value:str)->str: # type:ignore 
        value = value.strip()
        if not value :
            raise ValueError("Query cannot be empty ")
        return value

class JobAcceptedResponse(BaseModel):
    job_id: UUID
    status: str
    message: str
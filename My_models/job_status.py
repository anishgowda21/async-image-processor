from pydantic import BaseModel

class JobStatus(BaseModel):
    requestId: str
    status: str
    output_url: str
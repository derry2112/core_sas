from typing import List, Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[List[dict]] = None

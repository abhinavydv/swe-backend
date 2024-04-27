from pydantic import BaseModel


class FileID(BaseModel):
    file_id: str

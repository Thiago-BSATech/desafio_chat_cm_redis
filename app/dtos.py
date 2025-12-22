from pydantic import BaseModel

class ChatPublicRequest(BaseModel):
    username: str
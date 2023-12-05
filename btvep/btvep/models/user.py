from pydantic import BaseModel


class UserInDB(BaseModel):
    id: int
    request_count: int
    enabled: bool
    created_at: int
    updated_at: int
    is_admin: int

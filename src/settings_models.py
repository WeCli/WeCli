from pydantic import BaseModel


class SettingsUpdateRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    settings: dict

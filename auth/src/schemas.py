from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class Ticket(BaseModel):
    ticket : str

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class UserInDB(User):
    hashed_password: str
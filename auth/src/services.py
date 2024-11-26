from bcrypt import gensalt, hashpw, checkpw
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError
from os import environ
import jwt

class CryptographyService:

    @classmethod
    def verify(cls, plain_string : str, hashed_string : str)->bool:
        return checkpw(plain_string.encode(), hashed_string.encode())

    @classmethod
    def get_hash(cls, plain_string : str) -> bytes:
        return hashpw(plain_string.encode(), gensalt())
    
    
class TokenService:
    SECRET_KEY = environ.get(key = 'SECRET_KEY', default="defaultSECRET1234567890")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def verify_access_token(cls, token : str):
        try:
            data = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
        except InvalidTokenError:
            return False
        return data
    
    @classmethod
    def verify_ticket(cls, key : str, ticket:str):
        data = TokenService.verify_access_token(ticket)
        if data:
            ticket_id = data.get(key)
            return ticket_id
        return False
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError
import jwt

class CryptographyService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify(cls, plain_string, hashed_string):
        return cls.pwd_context.verify(plain_string, hashed_string)

    @classmethod
    def get_hash(cls, plain_string):
        return cls.pwd_context.hash(plain_string)
    
    

class TokenService:
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
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
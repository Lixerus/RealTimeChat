from fastapi.exceptions import HTTPException
from fastapi import status

class CredentialException(HTTPException):
    def __init__(self,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

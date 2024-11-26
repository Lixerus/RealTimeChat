from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from exceptions import CredentialException
from services import TokenService, CryptographyService
from storage import DBService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = TokenService.verify_access_token(token)
    if not payload:
        raise CredentialException()
    username: str = payload.get("sub")
    if username is None:
        raise CredentialException()
    user = await DBService.get_user(username=username)
    if user is None:
        raise CredentialException()
    return user

async def authenticate_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await DBService.get_user(form_data.username)
    print(user)
    if not user:
        raise CredentialException()
    if not CryptographyService.verify(form_data.password, user.hashed_password):
        raise CredentialException()
    return user
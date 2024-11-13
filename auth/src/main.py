from schemas import Token, User, TicketData, Ticket
from typing import Annotated
from fastapi import Depends, FastAPI, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from dependencies import get_current_active_user
from services import TokenService, CryptographyService
from storage import DBService
from exceptions import CredentialException
from message import AuthRpcConsumer
from contextlib import asynccontextmanager
import datetime
import uuid
# to get a string like this run:
# openssl rand -hex 32


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    await AuthRpcConsumer._connect()
    yield

middlewares = [
    Middleware(CORSMiddleware, allow_headers = ['*'], allow_origins = ['null'], allow_methods=["*"], allow_credentials = True)
]

app = FastAPI(lifespan=lifespan, middleware=middlewares)

@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.post("/ticket", status_code=201)
async def get_ticket(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Ticket:
    id = str(uuid.uuid4())
    print(f"ID {id}")
    ticket = TokenService.create_access_token({'id' : id}, expires_delta=datetime.timedelta(seconds=30))
    await DBService.add_ticket_id(id)
    print(f"TOKEN {ticket}")
    return Ticket(ticket=ticket)

async def authenticate_user(username: str, password: str):
    user = await DBService.get_user(username)
    if not user:
        return False
    if not CryptographyService.verify(password, user.hashed_password):
        return False
    return user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise CredentialException()
    access_token = TokenService.create_access_token(data={"sub": user.username})
    await DBService.add_to_logged(user.username, token = access_token)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/register")
async def register(login : Annotated[str, Body()], password : Annotated[str, Body()]):
    hashed_password = CryptographyService.get_hash(password)
    res = await DBService.save_user(login, hashed_password)
    return {"status" : f"{res}"}
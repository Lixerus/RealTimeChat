from fastapi import FastAPI, Depends, WebSocket, Query
from fastapi.websockets import WebSocketDisconnect
import uvicorn
from ws_manager import WsChatManager
from auth_rpc_client import AuthRpcClient
from typing import Annotated, Callable
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    await AuthRpcClient._connect()
    yield

middlewares = [
    Middleware(CORSMiddleware, allow_headers = ['*'], allow_origins = ['null'], allow_methods=["*"])
]
app = FastAPI(lifespan=lifespan, middleware=middlewares)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)


def get_auth_rpc_call():
    return AuthRpcClient.verify_ticket

async def get_message_handler():
    return WsChatManager.handle_message


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, ticket : Annotated[str, Query()],
    verify_func : Annotated[Callable, Depends(get_auth_rpc_call)],
    message_handler : Annotated[Callable, Depends(get_message_handler)]
    ):
    print(f"GOT {ticket}")
    result = await verify_func(ticket)
    print(result)
    if result != 'accept':
        await websocket.close()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            success = await message_handler(data)
            if not success:
                await websocket.close()
    except WebSocketDisconnect:
        WsChatManager.del_from_group_on_disconnect(websocket)

from fastapi import FastAPI, Depends, WebSocket, Query, Response
from fastapi.websockets import WebSocketDisconnect
from fastapi.exceptions import ValidationException
import uvicorn
from .ws_manager import WsChatManager
from .auth_rpc_client import AuthRpcClient, RpcStatuses
from .validation import WsMessage, WsMsgTypes
from .chat_client import ChatMessagesClient
from typing import Annotated, Callable
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.security import OAuth2PasswordBearer
from .cache_service import CacheService
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await AuthRpcClient._connect()
    await ChatMessagesClient._connect()
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

async def get_message_publish():
    return ChatMessagesClient.broadcast_msg


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, ticket : Annotated[str, Query()],
    verify_func : Annotated[Callable, Depends(get_auth_rpc_call)],
    publish_message : Annotated[Callable, Depends(get_message_publish)],
    cache_service : Annotated[CacheService, Depends()]
    ):
    result = await verify_func(ticket)
    if result != RpcStatuses.ACCEPT.value:
        return Response(status_code = 401)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = WsMessage(data)
            if message.msg_type == WsMsgTypes.NEW_MESSAGE_HEADER:
                group, username, text = message.get_message()
                await cache_service.update_group_cache(group, f'{username} {text}')
                await publish_message(group, username, text)
            else:
                prev_group, new_group = message.get_message()
                WsChatManager.switch_groups(websocket, prev_group, new_group)
                new_group_msgs = await cache_service.retreve_group_cahce(new_group)
                if new_group_msgs:
                    await websocket.send_json(data = new_group_msgs)
    except WebSocketDisconnect:
        print("Ws unexpectedly closed")
        WsChatManager.del_from_group_on_disconnect(websocket)
    except ValidationException as e:
        print(e.errors())
        await websocket.close(code=1003, reason="Bad message")
        WsChatManager.del_from_group_on_disconnect(websocket)

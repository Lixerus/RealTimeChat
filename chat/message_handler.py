from enum import Enum
from fastapi import WebSocket
from chat_client import ChatMessagesClient
from ws_manager import WsChatManager

class WsMsgHandler:
    class MsgTypes(Enum):
        MESSAGE = 'message'
        GROUP = 'group'

    message_types : MsgTypes = MsgTypes()
    group_manager : WsChatManager = WsChatManager

    @classmethod
    async def handle_message(cls, message : str, ws : WebSocket):
        tokens : list = message.split(' ')
        if tokens[0] not in cls.message_types:
            return False
        if tokens[0] == cls.message_types.MESSAGE:
            if tokens[1] in cls.group_manager._group_set and tokens[1] != 'null':
                return await ChatMessagesClient.broadcast_msg(tokens[1], tokens[2], tokens[3])
        elif tokens[0] == cls.message_types.GROUP:
            if tokens[1] in cls.group_manager._group_set and tokens[2] in cls.group_manager._group_set and len(tokens) == 3:
                return WsChatManager.switch_groups(ws, tokens[1], tokens[2])
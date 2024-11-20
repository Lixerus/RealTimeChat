from fastapi import WebSocket
from collections import defaultdict

class WsChatManager:
    _groups : dict[str,set[str]] = defaultdict(set)
    _group_set : set = {'group1','group2','group3','group4','group5','null'}

    @classmethod
    def add_to_group(cls, ws : WebSocket, group_name : str):
        cls._groups[group_name].add(ws)

    @classmethod
    def del_from_group(cls, ws : WebSocket, group_name : str)->bool:
        try:
            cls._groups[group_name].remove(ws)
        except KeyError:
            return False
        return True
    
    @classmethod
    def del_from_group_on_disconnect(cls, ws : WebSocket):
        for group in cls._groups.keys():
            if ws in cls._groups[group]:
                cls._groups[group].remove(ws)
                return True

    @classmethod
    def get_ws_in_group(cls, group_name:str) -> set:
        return cls._groups[group_name]
    
    @classmethod
    def switch_groups(cls, ws : WebSocket, prev_group  : str, new_group : str)->bool:
        validity = True
        if new_group == 'null':
            return False
        elif prev_group != 'null':
            validity = cls.del_from_group(ws, prev_group)
        if validity:
            cls.add_to_group(ws, new_group)
        return validity
    
    @classmethod
    def get_all_groups(cls):
        return cls._group_set
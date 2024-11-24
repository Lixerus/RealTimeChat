from enum import Enum
from fastapi.exceptions import ValidationException
from .ws_manager import WsChatManager
from re import findall

class WsMsgTypes(Enum):
    NEW_MESSAGE_HEADER = 'msg'
    GROUP_CHANGE_HEADER = 'grp'

class WsMessage:
    _all_groups : set = WsChatManager.get_all_groups()

    def __init__(self, message : str):
        try:
            self.tokens = message.split(' ',3)
            self.msg_type = WsMsgTypes(self.tokens[0])
            if self.msg_type == WsMsgTypes.NEW_MESSAGE_HEADER:
                self.validate_message()
            elif self.msg_type == WsMsgTypes.GROUP_CHANGE_HEADER:
                self.validate_group()
        except ValueError as e:
            raise ValidationException(errors=[e])

    def validate_message(self):
        try:
            assert len(self.tokens) == 4
            msg_group = self.tokens[1]
            assert msg_group in self._all_groups
            assert msg_group != 'null'
            username = self.tokens[2]
            text = self.tokens[3]
            self.validate_input(username)
            self.validate_input(text)
        except AssertionError as e:
            raise

    def validate_group(self):
        try:
            assert len(self.tokens) == 3
            past_group = self.tokens[1]
            new_group = self.tokens[2]
            assert past_group in self._all_groups
            assert new_group in self._all_groups
            assert (new_group != 'null' or past_group != 'null')
        except AssertionError as e :
            raise ValidationException(errors=[e])
        
    def validate_input(self, input:str):
        '''
            Simple search for tags. Approach with sanitization could be used.
        '''
        re_pattern = r'(?:<script>|</script>|<iframe>|</iframe>)'
        result = findall(re_pattern, input)
        assert len(result) == 0

    def get_message(self):
        return self.tokens[1:]
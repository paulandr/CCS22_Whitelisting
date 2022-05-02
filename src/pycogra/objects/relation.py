#!/usr/bin/env/python
import json
from src.pycogra.objects.message import Message
from src.pycogra.objects.component import Component


def contains_message(msg: Message, message_l: list) -> (bool, Message):
    assert(isinstance(msg, Message))
    assert(isinstance(message_l, list))

    for m in message_l:
        if m == msg:
            return True, m

    return False, None


class Relation(object):
    def __init__(self, src: Component, dst:Component):
        assert(isinstance(src, Component) and isinstance(dst, Component))
        self.src: Component = src
        self.dst: Component = dst
        self.messages = []

    def to_json(self, indent=4) -> json:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def __str__(self):
        return str(self.to_json())

    def __eq__(self, other):
        return self.src == other.src and self.src == other.dst

    def to_dict(self) -> dict:
        res_dict = {'src': self.src.get_id(), 'dst': self.dst.get_id(), 'messages': []}
        for m in self.messages:
            res_dict['messages'].append(m.to_dict())
        return res_dict

    def add_message(self, message: Message, check: bool=False):
        assert(isinstance(message, Message))
        if not check:
            self.messages.append(message)
        else:
            known, m = contains_message(message, self.messages)
            if known:
                m.inc_count(message.get_pdu_count())
            else:
                self.messages.append(message)

    def get_messages(self):
        return self.messages

    def message_count(self) -> int:
        result = 0
        for m in self.messages:
            result = result + m.get_pdu_count()
        return result

    def get_src_component(self) -> Component:
        return self.src

    def get_dst_component(self) -> Component:
        return self.dst
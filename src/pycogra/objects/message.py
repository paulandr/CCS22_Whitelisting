#!/usr/bin/env/python
import json
from src.pycogra.objects.address import valid_ipv4, valid_mac

MESSAGE_VAL_D = {
    'src': (str, None),
    'dst': (str, None),
    'mapped': (int, 0),
    'protocol': (int, None),
    'pdu': (int, None),
    'pduCount': (int, None),
    'transport_real': (int, None),
    'transport_virtual': (int, None)
}


class ProtocolID(object):
    def __init__(self, tp_id: int, pp_id: int):
        self.tr: int = tp_id
        self.pr: int = pp_id

    def to_dict(self) -> dict:
        result = {}
        for e in self.__dict__:
            result[e] = self.__dict__[e]
        return result

    def __str__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return hash(self) == hash(other)


class PduID(ProtocolID):
    def __init__(self, tp_id: int, pp_id: int, pdu_id: int):
        self.pdu = pdu_id
        super().__init__(tp_id, pp_id)


class Message(object):
    def __init__(self, **params):
        self.__dict__.update(params)
        for k in MESSAGE_VAL_D:
            # allows the definition of default values in MESSAGE_VAL_D that can be used when handling cogra files
            # with missing messages attributes (result of version changes).
            try:
                assert(k in self.__dict__)
            except AssertionError:
                assert(MESSAGE_VAL_D[k][1] is not None)
                self.__dict__[k] = MESSAGE_VAL_D[k][1]
            assert(type(self.__dict__[k]) == MESSAGE_VAL_D[k][0])

    def to_json(self, indent=4) -> json:
        return json.dumps(self, default=lambda o: o.__dict__, indent=indent, sort_keys=True)

    def to_dict(self) -> dict:
        return self.__dict__

    def get_pdu_count(self) -> int:
        return self.pduCount

    def inc_count(self, inc: int):
        self.pduCount += inc

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        to_hash = str(self.src) + str(self.dst) + str(self.protocol) + str(self.pdu) + \
                  str(self.transport_virtual) + str(self.transport_real)
        return hash(to_hash)

    def __str__(self):
        return str(self.to_json())

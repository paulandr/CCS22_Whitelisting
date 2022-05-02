#!/usr/bin/env/python
import re


def valid_mac(mac_string) -> bool:
    assert (isinstance(mac_string, str))
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_string.lower()):
        return True
    else:
        return False


def valid_ipv4(ipv4_string) -> bool:
    assert (isinstance(ipv4_string, str))
    if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ipv4_string.lower()):
        addr = ipv4_string.split('.')
        if len(addr) != 4:
            return False
        for octet in addr:
            if not octet.isdigit():
                return False
            i = int(octet)
            if i < 0 or i > 255:
                return False
        return True
    else:
        return False


def equal_ipv4_lists(a1: list, a2: list) -> bool:
    assert(len(a1) == 0 or valid_ipv4(a) for a in a1)
    assert(len(a2) == 0 or valid_ipv4(a) for a in a2)

    if len(a1) != len(a2):
        return False

    for a in a1:
        if a not in a2:
            return False

    return True


class AddrTuple(object):
    def __init__(self, src: str, dst: str):
        self.src: str = src
        self.dst: str = dst

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(self.src + "_" + self.dst)

    def __eq__(self, other):
        return hash(self) == hash(other)

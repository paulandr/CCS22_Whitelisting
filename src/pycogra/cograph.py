#!/usr/bin/env/python

import json

from src.pycogra.objects.component import Component
from src.pycogra.objects.relation import Relation
from src.pycogra.objects.message import Message
from src.pycogra.objects.address import valid_mac, valid_ipv4
from src.pycogra.objects.aggregation import RelationCount


def message_count(object_l: list):
    assert (type(object_l) == list)
    result: int = 0
    for o in object_l:
        assert (type(o) == Relation or type(o) == Message)
        if type(o) == Relation:
            result += o.message_count()
        else:
            result += o.get_pdu_count()
    return result


def print_components(component_l: list):
    to_print = ""
    for c in component_l:
        to_print += "> " + str(c) + "\n"
    to_print = to_print[:-1]
    print(to_print)


def contains_component(component: Component, component_l: list) -> (bool, Component):
    assert (isinstance(component_l, list))
    for c in component_l:
        assert (isinstance(c, Component))
        if c == component:
            return True, c
    return False, None


def contains_relation(src: Component, dst: Component, relation_l: list) -> (bool, Relation):
    assert (isinstance(relation_l, list))
    assert (isinstance(src, Component) and isinstance(dst, Component))
    for r in relation_l:
        if r.get_src_component() == src and r.get_dst_component() == dst:
            return True, r
    return False, None


class CoGraph(object):
    def __init__(self, cogra_dict: dict = None):
        self.components = []
        self.relations = []
        self.timestamp: int = 0

        if cogra_dict is not None:
            self.__dict__.update(cogra_dict)

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def relation_count(self) -> int:
        return len(self.relations)

    @property
    def component_id_l(self) -> list:
        result = []
        for c in self.components:
            result.append(c.get_id())
        return sorted(result)

    @property
    def message_count(self) -> int:
        return message_count(self.relations)

    @property
    def addresses(self) -> dict:
        result = {'mac': list(dict.fromkeys(self.get_mac_addresses())),
                  'ip': list(dict.fromkeys(self.get_ip_addresses()))}
        return result

    def to_dict(self) -> dict:
        result = {'components': [], 'relations': [], 'timestamp': str(self.timestamp)}
        for c in self.components:
            result['components'].append(c.to_dict())
        for r in self.relations:
            result['relations'].append(r.to_dict())
        return result

    def to_json(self, indent=4) -> json:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def aggregate_relations(self, aggregation_mode: str = 'pr', cmp_filter: Component = None) -> RelationCount:
        return RelationCount(self.relations)

    def get_mac_addresses(self, p_id: int = None) -> list:
        result = []
        for c in self.components:
            if p_id is None or p_id == c.get_id():
                mac = c.get_mac()
                if mac is not None and mac not in result:
                    result.append(mac)
                if p_id is not None:
                    break
        return result

    def get_ip_addresses(self, p_id: int = None) -> list:
        result = []
        for c in self.components:
            if p_id is None or p_id == c.get_id():
                ip_l = c.get_ip_list()
                for ip in ip_l:
                    if ip not in result:
                        result.append(ip)
                if p_id is not None:
                    break
        return result

    def get_addresses(self, p_id: int = None) -> list:
        return self.get_mac_addresses(p_id) + self.get_ip_addresses(p_id)

    def get_messages(self) -> list:
        result = []
        for r in self.relations:
            result = result + r.get_messages()
        return result

    def add_component(self, component: Component):
        assert (isinstance(component, Component))
        assert (self.get_component_by_id(component.get_id()) is None)

        (known, c) = contains_component(component, self.components)

        if known:
            print("add_component() INFO: graph already contains component: " + str(component))
            c.add_ip_l(component.get_ip_list())
            return

        if component.get_id() is None:
            component.set_id(self.get_next_free_component_id())

        self.components.append(component)

    def add_component_by_address(self, addr: str) -> Component:
        assert (valid_mac(addr) or valid_ipv4(addr))
        cmp_l = self.get_component_l_by_addr(addr)

        assert (len(cmp_l) <= 1)

        if len(cmp_l) == 1:
            return cmp_l[0]
        else:
            c: Component = Component()
            c.add_address(addr)
            c.set_id(self.get_next_free_component_id())
            self.components.append(c)
            return c

    def set_components(self, components: list):
        assert (isinstance(components, list))
        for c in components:
            assert (isinstance(c, Component))

        self.components.clear()
        self.components = components

    def get_component_by_id(self, p_id: int) -> Component:
        result = None
        for c in self.components:
            if c.id == p_id:
                result = c
                break

        return result

    def get_component_l_by_addr(self, address: str) -> list:
        result = []
        assert (valid_mac(address) or valid_ipv4(address))

        for c in self.components:
            if c.contains_address(address):
                result.append(c)

        return result

    def get_components(self) -> list:
        return self.components

    def get_relations(self) -> list:
        return self.relations

    def get_next_free_component_id(self) -> int:
        return 0 if len(self.components) is 0 else int(self.component_id_l[-1] + 1)

    def add_message(self, src_addr: str, dst_addr: str, protocol: int, pdu: int, pduCount: int,
                    transport_real: int, transport_virtual: int, mapped: int):

        cmp_src: Component = self.add_component_by_address(src_addr)
        cmp_dst: Component = self.add_component_by_address(dst_addr)

        msg: Message = Message(src=src_addr, dst=dst_addr, protocol=protocol, pdu=pdu, pduCount=pduCount,
                               transport_real=transport_real, transport_virtual=transport_virtual, mapped=mapped)

        known_rel, rel = contains_relation(cmp_src, cmp_dst, self.relations)
        if not known_rel:
            rel = Relation(cmp_src, cmp_dst)
            self.relations.append(rel)
        rel.add_message(msg, check=True)

    def add_relation_l(self, relations: list):
        assert (isinstance(relations, list))
        for r in relations:
            assert (isinstance(r, Relation))
            assert (r.get_src_component() in self.components and
                    r.get_dst_component() in self.components)
            self.relations.append(r)

    def set_relation_l(self, relations: list):
        assert (isinstance(relations, list))
        for r in relations:
            assert (isinstance(r, Relation))

        self.relations.clear()
        self.relations = relations

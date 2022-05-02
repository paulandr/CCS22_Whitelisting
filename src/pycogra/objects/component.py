import json
import copy
from src.pycogra.objects.address import valid_mac, valid_ipv4, equal_ipv4_lists
from src.pycogra.objects.cogra_types import DISCOVERY_MODE, DISCOVERY_MODE_REVERSE
from src.pycogra.objects.feature import Feature


class ComponentTimeStamp(object):
    def __init__(self, first_seen: int, last_seen: int):
        self.first_seen = first_seen
        self.last_seen = last_seen

    def to_dict(self) -> dict:
        return self.__dict__


class Component(object):
    def __init__(self, c_id: int = None, ts: dict = None, disc_mode = None,
                 mac: str = None, ip_l: list = None, feature_l:list = None, cmp_dict:dict = None):
        assert (c_id is None or isinstance(c_id, int))
        assert (ts is None or isinstance(ts, int))
        assert (disc_mode is None or disc_mode in DISCOVERY_MODE)
        assert (mac is None or isinstance(mac, str))
        assert (ip_l is None or isinstance(ip_l, list))
        assert (feature_l is None or isinstance(feature_l, list))

        self.id: int = c_id

        self.mac = None
        if mac is not None:
            self.set_mac(mac)

        self.ips = []
        if ip_l is not None:
            self.add_ip_l(ip_l)

        self.features = []
        if feature_l is not None:
            for f in feature_l:
                self.add_feature(f)

        self.t_sec = ComponentTimeStamp(0, 0)
        if ts is not None:
            self.t_sec.first_seen = ts['first_seen']
            self.t_sec.last_seen = ts['last_seen']

        self.discovered = DISCOVERY_MODE['DISC_MODE_NOT_SET']
        if disc_mode is not None:
            self.discovered = disc_mode

        if cmp_dict is not None:
            self.__dict__.update(cmp_dict)

    def contains_address(self, address: str) -> bool:
        assert(valid_mac(address) or valid_ipv4(address))
        if valid_mac(address):
            return False if self.mac is None else self.mac == address
        else:
            for a in self.ips:
                if a == address:
                    return True
            return False

    def get_id(self) -> int:
        return self.id

    def get_mac(self) -> str:
        return self.mac

    def get_ip_list(self) -> list:
        return self.ips

    def to_dict(self) -> dict:
        result = copy.deepcopy(self.__dict__)
        result['t_sec'] = result['t_sec'].to_dict()

        if self.mac is None:
            del result['mac']
        if len(self.ips) <= 0:
            del result['ips']
        if len(self.features) <= 0:
            del result['features']

        return result

    def add_ip_l(self, ipv4_l: list):
        assert (isinstance(ipv4_l, list) and (valid_ipv4(a) for a in ipv4_l))
        for a in ipv4_l:
            if a not in self.ips:
                self.ips.append(a)
        self.ips.sort()

    def set_id(self, c_id: int):
        assert (isinstance(c_id, int))
        self.id = c_id

    def set_mac(self, mac_string: str):
        assert (valid_mac(mac_string))
        self.mac = mac_string

    def add_address(self, addr: str):
        assert(valid_mac(addr) or valid_ipv4(addr))
        if valid_mac(addr):
            self.set_mac(addr)
        else:
            self.add_ip_l([addr])

    def add_feature(self, feature):
        if feature is None:
            return
        assert isinstance(feature, Feature)
        self.features.append(feature)

    def to_json(self, indent=4) -> json:
        return json.dumps(self, default=lambda o: o.__dict__, indent=indent)

    def __str__(self):
        return str(self.to_json())

    def __eq__(self, other):
        if self.mac is not None:
            return self.mac == other.mac
        else:
            return equal_ipv4_lists(self.ips, other.ips)

    def __hash__(self):
        h_l = sorted(self.ips)
        h_l.append(str(self.mac))

        h_s = ""
        for h in h_l:
            h_s += h
        return hash(h_s)


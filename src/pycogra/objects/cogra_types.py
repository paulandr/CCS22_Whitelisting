from enum import IntEnum


class LLC_PROTOCOL_ID(IntEnum):
    LLC_PROTO_CDP = 0,
    LLC_PROTO_HP = 1,
    LLC_PROTO_STP = 2,
    LLC_PROTO_ISO_COTP = 3,
    LLC_PROTO_ISO_ESIS = 4,
    LLC_PROTO_SIEMENS = 5,
    LLC_PROTO_NDP = 6 # nortel discovery protocol


# defined in u_transport_types.h
class HeaderTransportID(IntEnum):
    TRANS_ETHERNET = 0
    TRANS_LLC = 1
    TRANS_IP = 2
    TRANS_TCP = 3
    TRANS_UDP = 4


# defined in u_type.h
class HeaderRole(IntEnum):
    TYPE_UNKNOWN = 0
    TYPE_SWITCH_ROUTER = 1
    TYPE_CLIENT = 2
    TYPE_SERVER = 3
    TYPE_PRINTER = 4
    TYPE_MULTICAST = 5


# defined in u_classifier.h
class HeaderClassifier(IntEnum):
    CLASS_PROTO = 0
    CLASS_OUI = 1
    CLASS_DPI = 2
    CLASS_TCP = 3


# defined in component.h
class HeaderDiscoveryMode(IntEnum):
    DM_NOT_SET = 0
    DM_DIRECT = 1
    DM_INDIRECT = 2


# defined in u_feature.h
class HeaderFeatureType(IntEnum):
    FT_ROLE = 0
    FT_NAME = 1
    FT_OPERATING_SYSTEM = 2
    FT_OTHER = 3


# defined in u_ft_os.h
class OPERATING_SYSTEM_PLATFORM(IntEnum):
    UNIX_LINUX = 0,
    WINDOWS = 1


# defined in os.h
class WINDOWS_TYPE(object):
    def __init__(self, major, minor):
        self.major_version = major
        self.minor_version = minor


# defined in os.h
class UNIX_LINUX_TYPE(object):
    def __init__(self, distribution, kernel):
        self.distribution = distribution
        self.kernel = kernel


# defined in u_component.h
DISCOVERY_MODE = {
    'DISC_MODE_NOT_SET': 0,
    'DISC_MODE_DIRECT': 1,
    'DISC_MODE_INDIRECT': 2
}

DISCOVERY_MODE_REVERSE = {
    0: 'DISC_MODE_NOT_SET',
    1: 'DISC_MODE_DIRECT',
    2: 'DISC_MODE_INDIRECT'
}

TR_TYPES_TO_STR = {
    HeaderTransportID.TRANS_ETHERNET: "eth",
    HeaderTransportID.TRANS_LLC: "llc",
    HeaderTransportID.TRANS_IP: "ip",
    HeaderTransportID.TRANS_TCP: "tcp",
    HeaderTransportID.TRANS_UDP: "udp"
}


def tr_int_to_str(tr: int) -> str:
    return TR_TYPES_TO_STR[HeaderTransportID(tr)]

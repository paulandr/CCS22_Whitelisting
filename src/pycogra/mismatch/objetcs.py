import json
from src.pycogra.ie.importer import import_from_json
from src.pycogra.objects.aggregation import AggregationDict
from src.pycogra.objects.message import Message, ProtocolID
from src.pycogra.util.file import get_filename
from src.pycogra.mismatch.plot_conf import *
from src.pycogra.mismatch.measures import *
from enum import Enum, auto


class RelationKey(object):
    def __init__(self, src: str, dst: str):
        self.src: str = src
        self.dst: str = dst

    def __hash__(self):
        return hash(self.src + "_" + self.dst)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def to_dict(self):
        result = {}
        for e in self.__dict__:
            result[e] = self.__dict__[e]
        return result

    def __str__(self):
        return str(self.to_dict())


def dict_key_to_RelationKey(d_key: str) -> RelationKey:
    d = json.loads(d_key.replace('\'', '\"'))
    return RelationKey(src=d['src'], dst=d['dst'])


class MismatchAggregation(object):
    def __init__(self):
        self.count = 0
        self.addr = AggregationDict()  # unknown addresses
        self.src = AggregationDict()  # new sending devices
        self.dst = AggregationDict()  # sending devices addresses new destination
        self.tr = AggregationDict()  # new transport protocol used between sender and receiver
        self.pr = AggregationDict()  # new payload protocol used between sender and receiver
        self.pdu = AggregationDict()  # new pdu type used between sender and receiver

    @property
    def attributes(self) -> list:
        result = list(self.__dict__.keys())
        return result

    def get_aggregation_dict(self, key: str) -> AggregationDict:
        assert(key in self.__dict__.keys() and key != 'count')
        return self.__dict__[key]

    def get_summary(self) -> dict:
        result = {}
        for k in self.__dict__:
            if isinstance(self.__dict__[k], AggregationDict) is False:
                result[k] = self.__dict__[k]
            else:
                result[k] = {'message_count': self.__dict__[k].get_count(),
                             'instance_count': self.__dict__[k].get_instance_count()}

        return result

    def get_instances(self, attr_key: str = None) -> dict:
        result = {}
        if attr_key is None:
            for k in self.__dict__:
                if k == 'count':
                    continue
                result[k] = self.get_instances(attr_key=k)
        else:
            assert (attr_key in self.__dict__.keys())
            result = self.__dict__[attr_key].get_elements()
        return result

    def get_diff_count(self, fpr_base: int = None) -> list:
        result = [self.count, self.addr.get_count(), self.src.get_count(), self.dst.get_count(),
                  self.tr.get_count(), self.pr.get_count(), self.pdu.get_count()]

        if fpr_base is not None:
            for i in range(0, len(result)):
                result[i] = float((result[i] * 100) / fpr_base)

        return result

    def add_unknown(self, addr: str, count: int, cnt_global: bool = True):
        self.addr.insert(addr, count, count, b_count=cnt_global)
        if cnt_global:
            self.count += count

    def add_src_new(self, addr: str, count: int):
        self.src.insert(addr, count, count)
        self.count += count

    def add_src_dst_new(self, addr_src: str, addr_dst: str, count: int):
        src = self.dst.insert(addr_src, count, AggregationDict)
        src.insert(addr_dst, count, count)
        self.count += count

    def add_tr_new(self, addr_src: str, addr_dst: str, tr: int, count: int):
        src_dst = self.tr.insert(RelationKey(addr_src, addr_dst), count, AggregationDict)
        src_dst.insert(tr, count, count)
        self.count += count

    def add_pr_new(self, addr_src: str, addr_dst: str, tr: int, pr: int, count: int):
        src_dst = self.pr.insert(RelationKey(addr_src, addr_dst), count, AggregationDict)
        src_dst.insert(ProtocolID(tr, pr), count, count)
        self.count += count

    def add_pdu_new(self, addr_src: str, addr_dst: str, tr: int, pr: int, pdu: int, count: int):
        src_dst = self.pdu.insert(RelationKey(addr_src, addr_dst), count, AggregationDict)
        pr = src_dst.insert(ProtocolID(tr, pr), count, AggregationDict)
        pr.insert(pdu, count, count)
        self.count += count

    def to_dict(self):
        return {'count': self.count, PLOT_ELEM_DEV_ADDR: self.addr.to_dict(), PLOT_ELEM_DEV_SRC: self.src.to_dict(),
                PLOT_ELEM_DEV_DST: self.dst.to_dict(), PLOT_ELEM_COM_TR: self.tr.to_dict(),
                PLOT_ELEM_COM_PR: self.pr.to_dict(), PLOT_ELEM_COM_PDU: self.pdu.to_dict()}

    def __str__(self):
        return str(self.to_dict())


class MessageMismatchType(Enum):
    ADDR_SRC_DST_UNKNOWN = auto()
    ADDR_SRC_UNKNOWN = auto()
    ADDR_DST_UNKNOWN = auto()
    ADDR_SRC_NEW = auto()
    ADDR_DST_NEW = auto()
    TR_NEW = auto()
    PR_NEW = auto()
    PDU_NEW = auto()


class MessageAggregation(object):
    def __init__(self, msg_l: list, addr_l: list):
        assert(isinstance(msg_l, list))
        self.__source_addr = AggregationDict()
        self.__dst_addr = AggregationDict()

        for m in msg_l:
            src = self.__source_addr.insert(m.src, m.pduCount, AggregationDict, params='dst')
            dst = src.insert(m.dst, m.pduCount, AggregationDict, params='tr')
            tr = dst.insert(m.transport_real, m.pduCount, AggregationDict, params='pr')
            pr = tr.insert(ProtocolID(m.transport_virtual, m.protocol), m.pduCount, AggregationDict, params='pdu')
            pr.insert(m.pdu, m.pduCount, m.pduCount)
            self.__dst_addr.insert(m.dst, m.pduCount, m.pduCount)

        self.__addr = addr_l

    def get_addr(self) -> list:
        return self.__addr

    def to_dict(self) -> dict:
        return {'src': self.__source_addr.to_dict(), 'dst': self.__dst_addr.to_dict()}

    def contains_message(self, msg: Message, diff_a: MismatchAggregation) -> (bool, MessageMismatchType):
        s_addr = self.__source_addr.get_dict()

        if msg.src not in self.__addr:
            diff_a.add_unknown(msg.src, msg.pduCount)
            if msg.dst not in self.__addr:
                diff_a.add_unknown(msg.dst, msg.pduCount, False)
                return False, MessageMismatchType.ADDR_SRC_DST_UNKNOWN
            else:
                return False, MessageMismatchType.ADDR_SRC_UNKNOWN

        if msg.dst not in self.__addr:
            diff_a.add_unknown(msg.dst, msg.pduCount)
            return False, MessageMismatchType.ADDR_DST_UNKNOWN

        # return in case the source address is not part of the known sending devices
        if msg.src not in s_addr:
            diff_a.add_src_new(msg.src, msg.pduCount)
            return False, MessageMismatchType.ADDR_SRC_NEW

        dst_l = s_addr[msg.src].get_dict()

        # return in case the destination address is not addressed by the source device
        if msg.dst not in dst_l:
            diff_a.add_src_dst_new(msg.src, msg.dst, msg.pduCount)
            return False, MessageMismatchType.ADDR_DST_NEW

        tr_l = dst_l[msg.dst].get_dict()

        # return in case a new transport protocol is used
        if msg.transport_real not in tr_l:
            diff_a.add_tr_new(msg.src, msg.dst, msg.transport_real, msg.pduCount)
            return False, MessageMismatchType.TR_NEW

        pr_l = tr_l[msg.transport_real].get_dict()
        pr_id = ProtocolID(msg.transport_virtual, msg.protocol)

        # return in case a new payload protocol is used
        if pr_id not in pr_l:
            diff_a.add_pr_new(msg.src, msg.dst, msg.transport_virtual, msg.protocol, msg.pduCount)
            return False, MessageMismatchType.PR_NEW

        pdu_l = pr_l[pr_id].get_dict()

        # return in case a new pdu type is used
        if msg.pdu not in pdu_l:
            diff_a.add_pdu_new(msg.src, msg.dst, msg.transport_virtual, msg.protocol, msg.pdu, msg.pduCount)
            return False, MessageMismatchType.PDU_NEW

        # message is part of the corresponding communication graph...
        return True, None

    def __str__(self):
        return str(self.to_dict())


class MismatchGraphContainer(object):
    def __init__(self, file_cogra=None):
        self.cogra_file = file_cogra
        self.cogra_object = None
        self.component_count = None
        self.message_count = None

        if file_cogra is not None:
            self.cogra_object = import_from_json(self.cogra_file)
            self.component_count = self.cogra_object.component_count
            self.message_count = self.cogra_object.message_count

    @property
    def addresses(self):
        return self.cogra_object.get_addresses()

    @property
    def label(self):
        return get_filename(self.cogra_file)

    @property
    def messages(self):
        return self.cogra_object.get_messages()

    def get_graph_file(self) -> str:
        return self.cogra_file

    def to_dict(self) -> dict:
        result = {'cogra_src': self.cogra_file, 'component_count': self.component_count,
                  'message_count': self.message_count}

        return result

    def __str__(self):
        return str(self.to_dict())


# stores test graph and reference graphs and determines corresponding mismatches
class MismatchHandler(object):
    def __init__(self, cogra_test: str = None, cogra_ref: list = None, mode_reverse: bool = False, ):
        self.graph_test = None
        if cogra_test is not None:
            self.graph_test = MismatchGraphContainer(cogra_test)

        # If self.mode_reverse is True, the graph stored under self.graph_test is considered to be the reference graph.
        self.mode_reverse: bool = mode_reverse

        self.graph_references: dict = {}  # key: DiffGraphContainer, value: DiffAggregation)
        if cogra_ref is not None:
            for r in cogra_ref:
                self.add_reference_graph(r)

        self.diff_data: dict = {} # stores the data hold by self.graph_references in a dict
        self.metrics: dict = {}

    @property
    def reference_graph_count(self) -> int:
        return len(self.graph_references)

    @property
    def reference_graph_keys(self) -> list:
        result = []
        for k in self.graph_references.keys():
            result.append(k.cogra_file)
        result.sort()
        return result

    def get_reference_files(self) -> list:
        result = []
        for k in self.graph_references.keys():
            result.append(k.cogra_file)

        result.sort()
        return result

    def get_mismatch_aggregation(self, reference_file: str) -> MismatchAggregation:
        for k in self.graph_references.keys():
            if k.cogra_file == reference_file:
                return self.graph_references[k]
        return None

    def add_reference_graph(self, cogra_ref: str):
        rg = MismatchGraphContainer(cogra_ref)
        print("reference graph: " + rg.get_graph_file())
        rel_diff = MismatchAggregation()

        reference = MessageAggregation(rg.messages, rg.addresses)
        messages_to_test = self.graph_test.messages

        if self.mode_reverse:
            messages_to_test = rg.messages
            reference = MessageAggregation(self.graph_test.messages, self.graph_test.addresses)

        for m in messages_to_test:
            reference.contains_message(m, rel_diff)

        self.graph_references[rg] = rel_diff

    def to_dict(self) -> dict:
        result = {'mode_reverse': self.mode_reverse, 'graph': self.graph_test.to_dict(), 'differences': [],
                  'metrics': {}}
        for c in self.graph_references:
            result['differences'].append({'graph': c.to_dict(),
                                          'relation_diff': self.graph_references[c].to_dict()})

        if not self.metrics:
            self.__create_metrics()

        result['metrics'] = self.metrics

        return result

    def mismatch_data_to_dict(self) -> dict:
        if not self.diff_data:
            self.__create_diff_data_dict()
        return self.diff_data

    def get_metrics(self) -> dict:
        if not self.metrics:
            self.__create_metrics()
        return self.metrics

    def get_plot_axis_label(self) -> dict:
        result = {'x': "whitelist generation step", 'y': "mismatching packet rate [%]"}

        if self.mode_reverse is True:
            result['x'] = "sub-capture number"

        return result

    def __create_metrics(self):
        if len(self.metrics) > 0:
            self.metrics.clear()

        if self.reference_graph_count < 2 or self.mode_reverse:
            return

        if not self.diff_data:
            self.__create_diff_data_dict()

        for k_m in DEC_MEASURES:
            self.metrics[k_m] = {}

            for k_w in self.diff_data.keys():
                self.metrics[k_m][k_w] = DEC_MEASURES[k_m](self.diff_data[k_w])

    def __create_diff_data_dict(self):
        if len(self.diff_data) > 0:
            self.diff_data.clear()

        for i in range(0, len(PLOT_ELEMS_SINGLE)):
            self.diff_data[PLOT_ELEMS_SINGLE[i]] = []

        fpr_base = self.graph_test.message_count

        for k in self.graph_references:
            if self.mode_reverse:
                fpr_base = k.message_count

            values_curr = self.graph_references[k].get_diff_count(fpr_base=fpr_base)

            for i in range(0, len(PLOT_ELEMS_SINGLE)):
                self.diff_data[PLOT_ELEMS_SINGLE[i]].append(values_curr[i + 1])

    def __str__(self):
        return str(self.to_dict())

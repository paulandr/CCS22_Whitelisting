from src.pycogra.objects.message import Message, ProtocolID


class AggregationDict(object):
    def __init__(self, name='elems'):
        self.elems: dict = {}
        self.count: int = 0
        self.name = name

    def get_count(self) -> int:
        return self.count

    def get_instance_count(self) -> int:
        return len(self.elems)

    def insert(self, o_key, count: int, o_value, params=None, b_count: bool = True) -> object:
        if o_key not in self.elems:
            if isinstance(o_value, type):
                if params is None:
                    self.elems[o_key] = o_value()
                else:
                    self.elems[o_key] = o_value(params)
            else:
                self.elems[o_key] = o_value
        else:
            if isinstance(self.elems[o_key], int):
                self.elems[o_key] += count
        if b_count:
            self.count += count
        return self.elems[o_key]

    def to_dict(self) -> dict:
        elems = {}
        for k in self.elems:
            if type(self.elems[k]) == AggregationDict or type(self.elems[k]) == Message:
                elems[str(k)] = self.elems[k].to_dict()
            else:
                elems[str(k)] = self.elems[k]
        return {'count': self.count, self.name: elems}

    def get_elements(self) -> dict:
        result = {}
        for k in self.elems:
            if type(self.elems[k]) == AggregationDict or type(self.elems[k]) == Message:
                result[str(k)] = self.elems[k].get_elements()
            else:
                result[str(k)] = self.elems[k]
        return result

    def get_dict(self) -> dict:
        return self.elems

    def get_keys(self) -> list:
        return list(self.elems.keys())

    def __str__(self):
        return str(self.to_dict())

    def empty(self) -> bool:
        return not self.elems


def get_protocols(messages: list) -> AggregationDict:
    result = AggregationDict()
    for m in messages:
        p = ProtocolID(m.transport_virtual, m.protocol)
        result.insert(p, m.pduCount, m.pduCount)
    return result


class RelationCountID(object):
    def __init__(self, src_id: int, dst_id: int):
        self.src_id: int = src_id
        self.dst_id: int = dst_id

    def __hash__(self):
        return hash(str(self.src_id) + ":" + str(self.dst_id))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return str(self.src_id) + "->" + str(self.dst_id)


class RelationCount(object):
    def __init__(self, relations: list):
        assert (isinstance(relations, list) is True)
        self.pr_agg = {}
        self.max_pr_val = 0

        for r in relations:
            self.pr_agg[RelationCountID(r.src.id, r.dst.id)] = get_protocols(r.messages)
            self.pr_agg[RelationCountID(r.src.id, r.dst.id)].count = \
                len(self.pr_agg[RelationCountID(r.src.id, r.dst.id)].elems)

            if self.max_pr_val < self.pr_agg[RelationCountID(r.src.id, r.dst.id)].count:
                self.max_pr_val = self.pr_agg[RelationCountID(r.src.id, r.dst.id)].count

    def to_dict(self) -> dict:
        result = {'rel': {}, 'max': self.max_pr_val}
        for k in self.pr_agg:
            result['rel'][str(k)] = self.pr_agg[k].to_dict()
        return result

    def get_max_pr_relations(self) -> list:
        result = []
        for k in self.pr_agg:
            if self.pr_agg[k].count == self.max_pr_val:
                result.append(k)

        return result

    def __str__(self):
        return str(self.to_dict())

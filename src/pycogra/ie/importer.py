from src.pycogra.cograph import CoGraph
from src.pycogra.objects.message import Message
from src.pycogra.objects.relation import Relation
from src.pycogra.objects.component import Component
from src.pycogra.objects.feature import Feature
from src.pycogra.objects.cogra_types import HeaderFeatureType

import os
import json


def import_from_json(file: str) -> CoGraph:
    assert(os.path.isfile(file) and file.endswith(".json"))

    result = CoGraph()
    file = os.path.abspath(file)

    with open(file) as data_file:
        dt_json = json.load(data_file)

        relations = []

        for c in dt_json['components']:
            result.add_component(Component(cmp_dict=c))

        for r in dt_json['relations']:
            relations.append(dict_to_relation(r, result))
        result.set_relation_l(relations)
    data_file.close()
    return result


def dict_to_message(m: json) -> Message:
    return Message(**m)


def dict_to_relation(r: json, c: CoGraph) -> Relation:
    assert(isinstance(c, CoGraph))
    src = c.get_component_by_id(r['src'])
    dst = c.get_component_by_id(r['dst'])

    assert (src is not None and dst is not None)

    rel = Relation(src, dst)
    rel.messages = list(map(dict_to_message, r['messages']))
    return rel

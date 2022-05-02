import json, os, os.path
from src.pycogra.mismatch.objetcs import MismatchHandler, MismatchGraphContainer, MismatchAggregation, AggregationDict
from src.pycogra.objects.address import AddrTuple
from src.pycogra.objects.message import ProtocolID


def __init_dataset_dir(dir_in: str) -> (list, list):
    if not dir_in.endswith('/'):
        dir_in = dir_in + '/'

    diff_files = []
    diff_objects = []
    dataset_labels = []

    tmp_l = os.listdir(dir_in)
    for f in tmp_l:
        if f.endswith(".json"):
            dataset_labels.append(f[:-5])
            curr_file = dir_in + f
            print("INFO: appending " + curr_file + " to dataset.")
            diff_files.append(curr_file)

    diff_files.sort()
    dataset_labels.sort()

    for f in diff_files:
        diff_objects.append(import_from_json(f))

    return diff_objects, dataset_labels


def __init_dataset_dict(dataset_in):
    labels = []
    diff_objects = []

    for k in dataset_in:
        assert(type(k) == str)
        assert(os.path.isfile(dataset_in[k]))
        labels.append(k)
        diff_objects.append(import_from_json(dataset_in[k]))

    return diff_objects, labels


def init_dataset(dataset_in) -> (list, list):
    assert(type(dataset_in) == str or type(dataset_in) == dict)
    if type(dataset_in) == str:
        return __init_dataset_dir(dataset_in)
    else:
        return __init_dataset_dict(dataset_in)


def import_from_json(file_mismatch: str) -> MismatchHandler:
    assert (os.path.isfile(file_mismatch) and file_mismatch.endswith(".json"))

    with open(file_mismatch) as data_file:
        dt_json = json.load(data_file)

        result = MismatchHandler()

        result.mode_reverse = dt_json['mode_reverse']
        result.graph_test = __import_mismatch_graph_container(dt_json['graph'])
        result.graph_references = __import_mismatch_graphs(dt_json['differences'])
        result.metrics = dt_json['metrics']

    return result


def __import_mismatch_graph_container(dt: json) -> MismatchGraphContainer:
    result = MismatchGraphContainer()
    result.cogra_file = dt['cogra_src']
    result.component_count = dt['component_count']
    result.message_count = dt['message_count']
    return result


def __create_addr_tuple(dt: str) -> AddrTuple:
    addr = dt.split(', ')
    src = addr[0][9:]
    src = src[:-1]
    dst = addr[1][8:]
    dst = dst[:-2]
    return AddrTuple(src, dst)


def __create_protocol_id(dt: str) -> ProtocolID:
    id_l = dt.split(', ')
    tr = id_l[0][7:]
    pr = id_l[1][6:]
    pr = pr[:-1]
    return ProtocolID(int(tr), int(pr))


def __import_mismatch_aggregation(dt: json) -> MismatchAggregation:
    result = MismatchAggregation()
    result.count = dt['count']

    result.addr.count = dt['addr']['count']
    for e in dt['addr']['elems']:
        result.addr.elems[e] = dt['addr']['elems'][e]

    result.src.count = dt['src']['count']
    for e in dt['src']['elems']:
        result.src.elems[e] = dt['src']['elems'][e]

    result.dst.count = dt['dst']['count']
    for e in dt['dst']['elems']:
        result.dst.elems[e] = AggregationDict()
        result.dst.elems[e].count = dt['dst']['elems'][e]['count']
        for a in dt['dst']['elems'][e]['elems']:
            result.dst.elems[e].elems[a] = dt['dst']['elems'][e]['elems'][a]

    result.tr.count = dt['tr']['count']
    for e in dt['tr']['elems']:
        at = __create_addr_tuple(e)
        result.tr.elems[at] = AggregationDict()
        result.tr.elems[at].count = dt['tr']['elems'][e]['count']
        for t in dt['tr']['elems'][e]['elems']:
            result.tr.elems[at].elems[t] = dt['tr']['elems'][e]['elems'][t]

    result.pr.count = dt['pr']['count']
    for e in dt['pr']['elems']:
        at = __create_addr_tuple(e)
        result.pr.elems[at] = AggregationDict()
        result.pr.elems[at].count = dt['pr']['elems'][e]['count']
        for pr in dt['pr']['elems'][e]['elems']:
            pr_id = __create_protocol_id(pr)
            result.pr.elems[at].elems[pr_id] = dt['pr']['elems'][e]['elems'][pr]

    result.pdu.count = dt['pdu']['count']
    for e in dt['pdu']['elems']:
        at = __create_addr_tuple(e)
        result.pdu.elems[at] = AggregationDict()
        result.pdu.elems[at].count = dt['pdu']['elems'][e]['count']

        for pr in dt['pdu']['elems'][e]['elems']:
            pr_id = __create_protocol_id(pr)
            result.pdu.elems[at].elems[pr_id] = AggregationDict()
            result.pdu.elems[at].elems[pr_id].count = dt['pdu']['elems'][e]['elems'][pr]['count']
            for pdu in dt['pdu']['elems'][e]['elems'][pr]['elems']:
                result.pdu.elems[at].elems[pr_id].elems[pdu] = dt['pdu']['elems'][e]['elems'][pr]['elems'][pdu]

    return result


def __import_mismatch_graphs(dt: json) -> dict:
    result = {}
    for dg in dt:
        res_dg_key = __import_mismatch_graph_container(dg['graph'])
        result[res_dg_key] = __import_mismatch_aggregation(dg['relation_diff'])
    return result




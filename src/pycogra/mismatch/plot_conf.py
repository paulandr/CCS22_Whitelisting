# https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
PLOT_FILTER_MODE_WL = 'PF_WL'
PLOT_FILTER_MODE_BL = 'PF_BL'

PLOT_ELEM_DEV_ADDR = 'addr'
PLOT_ELEM_DEV_SRC = 'src'
PLOT_ELEM_DEV_DST = 'dst'
PLOT_ELEM_COM_TR = 'tr'
PLOT_ELEM_COM_PR = 'pr'
PLOT_ELEM_COM_PDU = 'pdu'

PLOT_ELEMS_AGGR_ALL = 'all'
PLOT_ELEMS_AGGR_DEV = 'dev'
PLOT_ELEMS_AGGR_COM = 'com'

PLOT_ELEMS_SINGLE = [PLOT_ELEM_DEV_ADDR, PLOT_ELEM_DEV_SRC, PLOT_ELEM_DEV_DST, PLOT_ELEM_COM_TR, PLOT_ELEM_COM_PR, PLOT_ELEM_COM_PDU]
PLOT_ELEMS_AGGR = [PLOT_ELEMS_AGGR_ALL, PLOT_ELEMS_AGGR_DEV, PLOT_ELEMS_AGGR_COM]

PLOT_AGGR = {PLOT_ELEMS_AGGR_ALL: PLOT_ELEMS_SINGLE,
             PLOT_ELEMS_AGGR_DEV: [PLOT_ELEM_DEV_ADDR, PLOT_ELEM_DEV_SRC, PLOT_ELEM_DEV_DST],
             PLOT_ELEMS_AGGR_COM: [PLOT_ELEM_COM_TR, PLOT_ELEM_COM_PR, PLOT_ELEM_COM_PDU]}

PLOT_ELEMS_CONF = {PLOT_ELEM_DEV_ADDR: {'color': '#ff0000', 'marker': None, 'label': 'addr', 'label_math': '$r_{U}$'},
                   PLOT_ELEM_DEV_SRC: {'color': '#ff6800', 'marker': 'o', 'label': 'src', 'label_math': '$R_{K_{src}}$'},
                   PLOT_ELEM_DEV_DST: {'color': '#ffa000', 'marker': 'v', 'label': 'dst', 'label_math': '$R_{K_{dst}}$'},
                   PLOT_ELEM_COM_TR: {'color': '#003cff', 'marker': '^', 'label': 'tp', 'label_math': '$R_{T}$'},
                   PLOT_ELEM_COM_PR: {'color': '#007bff', 'marker': '<', 'label': 'ap', 'label_math': '$R_{P}$'},
                   PLOT_ELEM_COM_PDU: {'color': '#00b9ff', 'marker': '<', 'label': 'pdu', 'label_math': '$R_{U}$'},
                   PLOT_ELEMS_AGGR_DEV: {'color': 'red', 'marker': None, 'label': 'dev', 'label_math': 'device-oriented'},
                   PLOT_ELEMS_AGGR_COM: {'color': 'darkblue', 'marker': None, 'label': 'com', 'label_math': 'comm.-oriented'},
                   PLOT_ELEMS_AGGR_ALL: {'color': 'darkgrey', 'marker': None, 'label': 'all', 'label_math': 'all'}}


def get_colors(plot_elems: list) -> list:
    assert(isinstance(plot_elems, list))
    result = []
    for k in plot_elems:
        assert(k in PLOT_ELEMS_CONF)
        result.append(PLOT_ELEMS_CONF[k]['color'])
    return result


def check_plot_elems(plot_elems: list) -> (list, dict):
    # remove duplicates
    plot_elems = list(dict.fromkeys(plot_elems))

    result_single: list = []
    result_aggr: list = []
    result_l: list = []
    result_d: dict = {}

    for e in plot_elems:
        if e is PLOT_ELEMS_AGGR_ALL:
            return [PLOT_ELEMS_AGGR_ALL], {PLOT_ELEMS_AGGR_ALL: PLOT_AGGR[PLOT_ELEMS_AGGR_ALL]}

        if e in PLOT_ELEMS_SINGLE:
            result_single.append(e)
        elif e in PLOT_ELEMS_AGGR:
            result_aggr.append(e)
        else:
            raise KeyError('Invalid plot element: ' + e)

    for s in result_single:
        ignore_s: bool = False
        for a in result_aggr:
            if s in PLOT_AGGR[a]:
                ignore_s = True
                continue
        if ignore_s:
            continue
        result_l.append(s)
        result_d[s] = [s]

    for a in result_aggr:
        result_d[a] = PLOT_AGGR[a]

    result_l.extend(result_aggr)
    return result_l, result_d



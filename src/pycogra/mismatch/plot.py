import matplotlib.pyplot as plt
import pandas as pd
from src.pycogra.mismatch.objetcs import MismatchHandler, MismatchAggregation
from src.pycogra.mismatch.plot_conf import *
from src.pycogra.mismatch.measures import fpr_measures
from src.pycogra.objects.cogra_types import tr_int_to_str


def __data_frame_from_element_filter(df_raw: pd.DataFrame, element_filter: list) -> pd.DataFrame:
    result = pd.DataFrame()
    l, d = check_plot_elems(element_filter)
    for k in d:
        df_t = pd.DataFrame(df_raw[d[k]])
        result[k] = df_t.sum(axis=1)
    return result


def __rename_data_frame(df: pd.DataFrame):
    renamed_cols = {}
    for col in df.columns:
        renamed_cols[col] = PLOT_ELEMS_CONF[col]['label_math']
    df.rename(columns=renamed_cols, inplace=True)


def plot_single_dataset(data_in: MismatchHandler, plot_elems: list = None, file_out: str = None,
                        figure_title: str = None, notebook: bool = False, p_ax = None) -> pd.DataFrame:
    assert(plot_elems is None or isinstance(plot_elems, list))

    # function is called from a notebook. the figure has to be cleared to prevent overlays in case of multiple
    # subsequent calls
    if notebook and not p_ax:
        plt.clf()

    axix_label = data_in.get_plot_axis_label()
    df_raw = pd.DataFrame(data_in.mismatch_data_to_dict())

    if plot_elems is None:
        df = df_raw
    else:
        df = __data_frame_from_element_filter(df_raw, plot_elems)

    count_row = df.shape[0]
    ax = p_ax or plt.gca()

    colors = get_colors(list(df.keys()))
    __rename_data_frame(df)

    # barplot
    df.plot(ax=ax, kind='bar', stacked=True, width=0.75, color=colors, legend=bool(not p_ax))

    # add simple lineplot
    ax.plot(df.sum(axis=1))

    # axis configuration
    plt.xticks(ticks=list(range(count_row)), labels=list(range(1, count_row + 1)))
    if not p_ax:
        plt.xlabel(axix_label['x'])
        plt.ylabel(axix_label['y'])

    if figure_title is not None:
        plt.title(figure_title)

    if file_out is not None:
        plt.savefig(file_out)
        print("Plot is saved under \"" + file_out + "\"")

    if not notebook:
        plt.show()

    return df


def lineplot_dataset(data_in: list, labels: list, plot_elems: list = None, file_out: str = None,
                     notebook: bool = False):
    assert(isinstance(data_in, list))
    assert(len(data_in) == len(labels))
    assert(plot_elems is None or isinstance(plot_elems, list))

    # axis configuration
    axix_label = data_in[0].get_plot_axis_label()

    df = pd.DataFrame()
    count: int = 0
    for dh in data_in:
        assert(isinstance(dh, MismatchHandler))
        df_t_raw = pd.DataFrame(dh.mismatch_data_to_dict(), index=list(range(1, dh.reference_graph_count + 1)))
        if plot_elems is None:
            df_t = df_t_raw
        else:
            df_t = __data_frame_from_element_filter(df_t_raw, plot_elems)

        df[labels[count]] = df_t.sum(axis=1)
        count = count+1

    # simple lineplot
    df.plot()
    plt.xlabel(axix_label['x'])
    plt.ylabel(axix_label['y'])

    if file_out is not None:
        plt.savefig(file_out)
        print("Plot is saved under \"" + file_out + "\"")

    if not notebook:
        plt.show()


def boxplot_dataset(data_in: list, labels: list, plot_elems: list = None, notebook: bool = False):
    assert(isinstance(data_in, list))
    assert(len(data_in) == len(labels))
    assert(plot_elems is None or isinstance(plot_elems, list))

    df_boxplot = pd.DataFrame()

    count: int = 0
    for dh in data_in:
        assert (isinstance(dh, MismatchHandler))
        df_t_raw = pd.DataFrame(dh.mismatch_data_to_dict(), index=list(range(1, dh.reference_graph_count + 1)))
        if plot_elems is None:
            df_t = df_t_raw
        else:
            df_t = __data_frame_from_element_filter(df_t_raw, plot_elems)

        dec = fpr_measures(df_t.sum(axis=1).to_list())
        df_boxplot[labels[count]] = dec['data']

        count = count + 1

    df_boxplot.boxplot(rot=45)
    plt.xlabel("dataset number")
    plt.ylabel("mismatching packet rate decrease [%]")

    plt.show()


def __create_instance_label(data_in: MismatchHandler, rg_filter: list = None) -> (list, list):
    result_rg_keys: list = []
    result_x_ax_label: list = []

    rg_keys_t = data_in.reference_graph_keys

    if rg_filter is not None:
        for i in rg_filter:
            result_rg_keys.append(rg_keys_t[i])
            result_x_ax_label.append(i + 1)
    else:
        result_rg_keys = rg_keys_t
        result_x_ax_label = list(range(1, len(rg_keys_t) + 1))

    return result_rg_keys, result_x_ax_label


def __create_src_dst_key(k_src: str, k_dst: str) -> str:
    return str(k_src + ' -> ' + k_dst)


def __create_tr_key(k_src_dst: str, k_tr: str) -> str:
    addr_l = k_src_dst.split(', ')
    result = addr_l[0][9:-1] + ' -> ' + addr_l[1][9:-2] + " (" + tr_int_to_str(int(k_tr)) + ")"
    return result


def __create_pr_key(k_src_dst: str, k_tr_pr: str) -> str:
    addr_l = k_src_dst.split(', ')
    pr_l = k_tr_pr.split(', ')
    tr_id = pr_l[0][7:]
    pr_id = pr_l[1][6:-1]

    result = addr_l[0][9:-1] + ' -> ' + addr_l[1][8:-2] + " [" + tr_int_to_str(int(tr_id)) + "(" + pr_id + ")]"
    return result


def __create_pdu_key(k_src_dst: str, k_tr_pr: str, k_pdu: str) -> str:
    return __create_pr_key(k_src_dst, k_tr_pr) + ': ' + k_pdu


def barplot_instances(data_in: MismatchHandler, instance_key: str, instance_index: list = None, notebook: bool = False) \
        -> pd.DataFrame:
    assert (isinstance(data_in, MismatchHandler))
    assert (instance_key in PLOT_ELEMS_SINGLE)

    rg_keys, x_ax_label = __create_instance_label(data_in, instance_index)
    inst_l: list = []
    inst_d_l: list = []

    for k in rg_keys:
        da: MismatchHandler = data_in.get_mismatch_aggregation(k)
        id: dict = da.get_instances(instance_key)

        d_tmp: dict = {}

        for k_addr in id:
            if instance_key == PLOT_ELEM_DEV_ADDR or instance_key == PLOT_ELEM_DEV_SRC:
                inst_l.append(k_addr)
            elif instance_key == PLOT_ELEM_DEV_DST:
                for k_dst in id[k_addr]:
                    k = __create_src_dst_key(k_addr, k_dst)
                    inst_l.append(k)
                    d_tmp[k] = id[k_addr][k_dst]
            else:
                for k_tr_pr in id[k_addr]:
                    if instance_key == PLOT_ELEM_COM_TR:
                        k = __create_tr_key(k_addr, k_tr_pr)
                        inst_l.append(k)
                        d_tmp[k] = id[k_addr][k_tr_pr]
                    elif instance_key == PLOT_ELEM_COM_PR:
                        k = __create_pr_key(k_addr, k_tr_pr)
                        inst_l.append(k)
                        d_tmp[k] = id[k_addr][k_tr_pr]
                    else:
                        for k_pdu in id[k_addr][k_tr_pr]:
                            k = __create_pdu_key(k_addr, k_tr_pr, k_pdu)
                            inst_l.append(k)
                            d_tmp[k] = id[k_addr][k_tr_pr][k_pdu]

        if instance_key == PLOT_ELEM_DEV_ADDR or instance_key == PLOT_ELEM_DEV_SRC:
            inst_d_l.append(id)
        else:
            inst_d_l.append(d_tmp)

    data_dict = dict.fromkeys(inst_l, [])

    if not data_dict:
        return None

    for k in data_dict:
        val_l = []
        for d in inst_d_l:
            if k in d:
                val_l.append(d[k])
            else:
                val_l.append(0)
        data_dict[k] = val_l

    df: pd.DataFrame = pd.DataFrame(data_dict)
    df.plot.bar(stacked=True)
    plt.xticks(ticks=list(range(len(df.index))), labels=x_ax_label)

    axix_label = data_in.get_plot_axis_label()
    plt.xlabel(axix_label['x'])
    plt.ylabel('number of mismatching packets')

    if not notebook:
        plt.show()

    return df


def barplot_index(data_in: MismatchHandler, index: int, plot_elems: list = None, notebook: bool = False, p_ax = None) \
        -> pd.DataFrame:
    assert (plot_elems is None or isinstance(plot_elems, list))

    # function is called from a notebook. the figure has to be cleared to prevent overlays in case of multiple
    # subsequent calls
    if notebook and not p_ax:
        plt.clf()

    axix_label = data_in.get_plot_axis_label()
    df_raw = pd.DataFrame(data_in.mismatch_data_to_dict())

    if plot_elems is None:
        df_abs = df_raw.loc[[index]]
    else:
        df_abs = __data_frame_from_element_filter(df_raw, plot_elems).loc[[index]]

    colors = get_colors(list(df_abs.keys()))
    __rename_data_frame(df_abs)

    value_sum = df_abs.sum(axis=1)

    values_abs = df_abs.values.tolist()[0]
    values_rel = {}
    cols = list(df_abs.keys())
    for i in range(0, len(values_abs)):
        values_rel[cols[i]] = [float((values_abs[i] * 100) / value_sum)]

    df_rel = pd.DataFrame(data=values_rel)
    df_rel.index = [index+1]

    ax = p_ax or plt.gca()

    # barplot
    df_rel.plot(ax=ax, kind='bar', stacked=True, width=0.75, color=colors, legend=bool(not p_ax))

    if not p_ax:
        plt.xlabel(axix_label['x'])
        plt.ylabel('mismatching packets [%]')

    if not notebook:
        plt.show()
    return df_rel


def dataset_subfigures(data_in: list, labels: list, plot_elems_l: list = None, file_out: str = None,
                       last_step_only: bool = False, notebook: bool = False, figsize: tuple = None):
    assert(isinstance(data_in, list))
    assert(len(data_in) == len(labels))
    assert(plot_elems_l is None or isinstance(plot_elems_l, list))

    elem_filter_count: int = 1
    if plot_elems_l is not None:
        elem_filter_count = len(plot_elems_l)

    dataset_count = len(data_in)
    cols_count: int = dataset_count
    rows_count: int = elem_filter_count

    figsize = figsize
    if figsize is None:
        figsize = (3*cols_count, 4*rows_count)

    fig, axs = plt.subplots(nrows=rows_count, ncols=cols_count, sharex='all', figsize=figsize)
    figure_count = dataset_count * elem_filter_count
    for i in range(0, figure_count):
        df_index: int = i % dataset_count
        pef_index: int = i // dataset_count

        if plot_elems_l:
            pe = plot_elems_l[pef_index]
        else:
            pe = None

        if rows_count == 1:
            a = axs[i]
        else:
            a = axs[pef_index][df_index]

        if not last_step_only:
            plot_single_dataset(data_in=data_in[df_index], plot_elems=pe, notebook=notebook, p_ax=a)
        else:
            barplot_index(data_in=data_in[df_index], index=data_in[df_index].reference_graph_count - 1, plot_elems=pe,
                          notebook=notebook, p_ax=a)

    if rows_count > 1:
        for ax, l in zip(axs[0], labels):
            ax.set_title(l)

        lines = []
        lines_label = []
        labels = []

        axes = []
        for a in axs:
            axes.append(a[0])
        for ax in axes:
            ax_line, ax_label = ax.get_legend_handles_labels()

            for l in ax_line:
                if l.get_label() not in lines_label:
                    lines_label.append(l.get_label())
                    lines.append(l)

            for l in ax_label:
                if l not in labels:
                    labels.append(l)

        fig.legend(lines, labels, loc='right')

    else:
        for ax, l in zip(axs, labels):
            ax.set_title(l)

        lines = []
        lines_label = []
        labels = []

        for ax in axs:
            ax_line, ax_label = ax.get_legend_handles_labels()

            for a in ax_line:
                if a.get_label() not in lines_label:
                    lines_label.append(a.get_label())
                    lines.append(a)

            for a in ax_label:
                if a not in labels:
                    labels.append(a)

        fig.legend(lines, labels, loc='right')

    axix_label = data_in[0].get_plot_axis_label()

    label_x = axix_label['x']
    label_y = axix_label['y']
    if last_step_only:
        label_y = 'mismatching packets [%]'

    if rows_count > 1:
        plt.setp(axs[-1, :], xlabel=label_x)
        plt.setp(axs[:, 0], ylabel=label_y)
    else:
        plt.setp(axs[0], ylabel=label_y)


    #plt.xlabel(axix_label['x'])
    fig.tight_layout()

    if file_out is not None:
        plt.savefig(file_out)
        print("Plot is saved under \"" + file_out + "\"")

    if not notebook:
        plt.show()

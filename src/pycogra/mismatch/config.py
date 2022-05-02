from src.ui.cli import file_dir_parse, file_parse
import argparse

from src.pycogra.mismatch.plot_conf import PLOT_ELEMS_SINGLE, PLOT_ELEMS_AGGR

def init_arg_parser(p):
    assert (isinstance(p, argparse.ArgumentParser))
    subparsers = p.add_subparsers()

    choices_filter = PLOT_ELEMS_SINGLE.copy()
    choices_filter.extend(PLOT_ELEMS_AGGR)

    parser_single = subparsers.add_parser('single')
    parser_single.add_argument('diff_input', help='dictionary containing cogra json files or previously generated '
                                                  'diff json file', type=file_parse)
    parser_single.add_argument('-f', '--f', nargs='+', choices=choices_filter, help='plot filter')
    parser_single.add_argument('-o', '--o', nargs='?', metavar='<output_file>', help='output file')
    parser_single.add_argument("-r", '--reverse', action="store_true", help='run in reverse mode '
                                                                            '(reference graph is specified by the '
                                                                            'chosen test graph). ')

    parser_dataset = subparsers.add_parser('dataset')
    parser_dataset.add_argument('dict_diff', help='dictionary containing input diff json files', type=file_dir_parse)
    parser_dataset.add_argument('-f', '--f', nargs='+', choices=choices_filter, help='plot filter')
    parser_dataset.add_argument('-o', '--o', nargs='?', metavar='<output_file>', help='output file')

    parser_investigate = subparsers.add_parser('investigate')
    parser_investigate.add_argument('dict_inv', help='dictionary containing input diff json files', type=file_parse)
    parser_investigate.add_argument('-o', '--o', nargs='?', metavar='<output_file>', help='output file')
    parser_investigate.add_argument("-r", '--reverse', action="store_true", help='run in reverse mode '
                                                                            '(reference graph is specified by the '
                                                                            'chosen test graph). ')


PROMPT_STR_GET_TEST_FILE = "Specify cogra test file. " \
                          "(Remeining cogra files will be sequentially used as graph reference.)"

PROMPT_STR_GET_INV_FILE = "Specify diff file for further investigation."
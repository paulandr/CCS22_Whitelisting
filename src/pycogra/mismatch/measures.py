import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def kmeans(data_in: pd.DataFrame, n_cluster: int = 3) -> list:
    X = np.array(data_in)
    kmeans = KMeans(n_clusters=n_cluster, random_state=0).fit(X)
    return kmeans.labels_


def _gini(x: list) -> float:
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad / np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad

    return g


def _gini_ap(x: list) -> float:
    # efforts increasing order of list element values!
    x.sort()

    n: int = len(x)

    s1: int = 0
    for i in range(1, n+1):
        s1 += i * x[i-1]
    s1 = 2*s1

    s2: int = 0
    for v in x:
        s2 += v
    s2 = n * s2

    g: float = (s1/s2) - ((n+1)/n)
    return g

'''
def gini(x: list, normed: bool = False) -> dict:
    mpr_dec_l = fpr_decrease(x)['absolut']
    g_mpr = _gini(x)
    g_mpr_dec = _gini(mpr_dec_l)

    if normed:
        n_1: int = len(x)
        n_2: int = len(mpr_dec_l)
        g_mpr = g_mpr * (n_1 / (n_1-1))
        g_mpr_dec = g_mpr_dec * (n_2 / (n_2-1))

    return {'g_mpr': g_mpr, 'g_mpr_dec': g_mpr_dec}
'''


def gini(x: list) -> dict:
    mpr_dec_l = fpr_decrease(x)['absolut']
    n = len(mpr_dec_l)
    g = {'g_mpr': _gini(x), 'g_mpr_dec': _gini(mpr_dec_l)}
    return {'g_mpr': g['g_mpr'], 'g_mpr_dec': g['g_mpr_dec'], 'g_mpr_dec_normed': g['g_mpr_dec'] * (n/(n-1))}


def fpr_decrease(data_in: list) -> dict:
    result = {'absolut': [], 'normed': []}

    base: float = data_in[0]
    for i in range(0, len(data_in) - 1):
        curr_dec: float = data_in[i] - data_in[i + 1]
        curr_dec_normed: float = (data_in[i] - data_in[i + 1]) / base
        result['absolut'].append(curr_dec)
        result['normed'].append(curr_dec_normed)

    return result


def fpr_measures(data_in: list) -> dict:
    dt_dec_l = fpr_decrease(data_in)

    dec_mean_abs = float(np.mean(dt_dec_l['absolut']))
    dec_mean_normed = float(np.mean(dt_dec_l['normed']))
    dec_std_abs = float(np.std(dt_dec_l['absolut']))
    dec_std_normed = float(np.std(dt_dec_l['normed']))
    dec_varC = float(dec_std_abs/dec_mean_abs)

    jumps = 0
    jump_base = float(dec_mean_abs * dec_varC)

    for i in range(0, len(dt_dec_l['absolut'])):
        if dt_dec_l['absolut'][i] > jump_base:
            jumps = jumps + 1

    return {'fpr_mean': float(np.mean(data_in)),
            'fpr_std': float(np.std(data_in)),
            'dec_mean': {'absolut': dec_mean_abs, 'normed': dec_mean_normed},
            'dec_std': {'absolut': dec_std_abs, 'normed': dec_std_normed},
            'dec_varC': dec_varC,
            'jump_rate': float(jumps/len(dt_dec_l['absolut'])), 'data': dt_dec_l
            }


DEC_MEASURES = {'fpr_decrease': fpr_measures, 'gini': gini}
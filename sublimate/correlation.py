import pandas as pd
import numpy as np


def corr_shift(x, y, x_shift=0, y_shift=0):
    """compute the correlation with shift

    Args:
        x (series): first series
        y (series): second series
        x_shift (int, optional): shift of first series. Defaults to 0.
        y_shift (int, optional): shift of second series. Defaults to 0.

    Returns:
        float: correlation
    """
    return x.shift(x_shift).corr(y.shift(y_shift))


def shift(df, shift_map=None):
    """shift the dataframe

    Args:
        df (dataframe): origin dataframe
        shift_map (dict, optional): mapping of shift for columns of dataframe. Defaults to None.

    Returns:
        dataframe: shiftted dataframe
    """
    if shift_map is not None:
        df = df.copy()
        min_lag = min(0, min(shift_map.values()))
        max_lead = max(0, max(shift_map.values()))
        df = df.reindex(df.index.union(df.index.shift(min_lag)).union(df.index.shift(max_lead)))
        for k, v in shift_map.items():
            df[k] = df[k].shift(v)
        return df
    else:
        return df


def max_tp(x, y, relation=None, shift_direction='lead', max_shift=8):
    """compute max correlation with lags

    Args:
        x (series): first series
        y (series): second series
        relation (int, optional): type of relation: positive relation(+1) and negative relation(-1). Defaults to None.
        shift_direction (str, optional): direction of shift ('lead'/'lag'/'sync'). Defaults to 'lead'.
        max_shift (int, optional): max periods of shift. Defaults to 8.

    Returns:
        int, float: max correlation periods, max correlation
    """
    relation_map = dict()
    if shift_direction == 'lead':
        for k in range(0, max_shift + 1):
            relation_map[str(k)] = x.shift(k).corr(y)
    elif shift_direction == 'lag':
        for k in range(- max_shift, 1):
            relation_map[str(k)] = x.shift(k).corr(y)
    elif shift_direction == 'sync':
        relation_map = {"0": x.corr(y)}
    else:
        for k in range(-max_shift, max_shift + 1):
            relation_map[str(k)] = x.shift(k).corr(y)
    
    if relation:
        relation_map_dir = {key:val for key, val in relation_map.items() if np.sign(relation)*val > 0}
    else:
        relation_map_dir = relation_map
    relation_map_abs = {key:abs(val) for key, val in relation_map_dir.items()}
    opt_shift = max(relation_map_abs, key=relation_map_abs.get)
    opt_corr = relation_map_dir[opt_shift]
    return opt_shift, opt_corr

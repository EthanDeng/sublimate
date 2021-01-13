import numpy as np
import pandas as pd

freq_mapping = {'A': 365, 'Y': 365, 'Q': 120, 'M': 30, 'W': 7, 'D': 1}
period_mapping = {'A': 1, 'Y': 1, 'Q': 4, 'M': 12, 'W': 52, 'D': 365}


def infer_freq(df):
    """infer frequency of dataframe

    Args:
        df (dataframe): origin dataframe 

    Returns:
        str: frequency, 'D', 'W', 'M', 'Q', 'Y', 'A'

    Examples:

        >>> data = pd.DataFrame(data=np.random.rand(5),
                        index=pd.date_range('2018-01-01', periods=5, freq='M'),
                        columns=['random'])
        >>> freq = infer_freq(data)
        >>> print(freq)
        {'random': 'M'}
    """
    freq_map = dict()
    for col in df.columns:
        temp = df[col].dropna()
        day_gaps = np.min(np.diff(temp.index.values)) / np.timedelta64(1, 'D')
        if day_gaps == 1:
            freq = 'D'
        elif 28 <= day_gaps <= 31:
            freq = 'M'
        elif 89 <= day_gaps <= 92:
            freq = 'Q'
        elif 365 <= day_gaps <= 366:
            freq = 'A'
        else:
            freq = None
        freq_map[col] = freq
    return freq_map


def resample_series(x, target_freq, agg_type='mean'):
    """resample series to targe_freq

    Args:
        x (dataframe): single column dataframe with datetime index
        target_freq (str): target frequency
        agg_type (str, optional): aggregate type. Defaults to 'mean'.

    Returns:
        dataframe: resampled dataframe
    """
    self_freq = list(infer_freq(x).values())[0]
    self_name = list(infer_freq(x).keys())[0]
    if freq_mapping[self_freq] <= freq_mapping[target_freq]:
        res = x.resample(target_freq).agg({self_name: agg_type})
    else:
        res = pd.DataFrame()
    return res


def resample_df(df, target_freq, agg_map):
    """resample dataframe to target_freq

    Args:
        df (dataframe): origin dataframe
        target_freq (str): target frequency
        agg_map (dict): resample methods mapping

    Returns:
        dataframe: resampled dataframe
    """
    res = pd.DataFrame()
    for col in df.columns:
        agg_type = agg_map[col]
        temp = resample_series(df[[col]], target_freq=target_freq, agg_type=agg_type)
        res = pd.merge(res, temp, left_index=True, right_index=True, how='outer')
        return res


def cal_change_series(x, cal_type='同比', ratio=True):
    """calculate the change of series

    Args:
        x (dataframe): single column dataframe with datetime index
        cal_type (str, optional): calculation type. Defaults to '同比'.
        ratio (bool, optional): compute ratio or not. Defaults to True.

    Returns:
        dataframe: dataframe with `cal_type`
    """
    x = x.copy()
    x.dropna(inplace=True)
    self_freq = list(infer_freq(x).values())[0]
    if (cal_type == '同比') & ratio:
        res = x.pct_change(period_mapping[self_freq])
    elif (cal_type == '同比') & (ratio is False):
        res = x.diff(period_mapping[self_freq])
    elif ratio:
        res = x.pct_change(1)
    else:
        res = x.diff(1)
    return res


def cal_change_df(df, cal_map, ratio_map):
    """calculate the changes of dataframe

    Args:
        df (dataframe): origin dataframe
        cal_map (dict): calculate mapping of df columns
        ratio_map (dict): ratio mapping of df columns

    Returns:
        dataframe: dataframe with `cal_type`
    """
    res = pd.DataFrame()
    for col in df.columns:
        cal_type = cal_map[col]
        ratio_type = ratio_map[col]
        temp = cal_change_series(df[[col]], cal_type, ratio_type)
        res = pd.merge(res, temp, left_index=True, right_index=True, how='outer')
    return res
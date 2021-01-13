import pandas as pd
from WindPy import w
import datetime as dt
import re

def wind_feature(code, start_date=None, end_date=None, keep=False, output='wide'):
    """ 从 wind 获取数据

    本函数为方便从 wind 取出单个指标或者复合指标的数据，复合指标可以由单指标复合得到，输出数据可选为长型或者宽型数据。

    Args:
        code (str): 指标 ID，可以是复合指标
        start_date (str): 获取数据的起始时间，默认为去年 1 月 1 日
        end_date (str): 获取数据的结束时间，不填写则为最新（today）
        keep (bool): 是否保留衍生指标的原指标
        output (str): 返回的数据显示类型，可以为 wide 或者 long

    Returns:
        dataframe: 单个指标或者复合指标的数据框，长型或者宽型

    Examples:
        1. 单指标，获取 2019 年以来上海优质写字楼租金（S2707241），以 wide 形式返回

        >>> wind_feature(code='S2707241')
                        S2707241
            2019-03-31    298.90
            2019-06-30    296.80
            2019-09-30    293.83
            2019-12-31    318.81
        
        2. 获取特定时间区间内的数据

        >>> wind_edb(code='S2707241', start_date='2019-01-01', end_date='2019-06-30')
                         S2707241
            2019-03-31    298.90
            2019-06-30    296.80

        3. 复合指标，获取 2019 年以来上海和北京优质写字楼租金（S2707241、S2707194）的平均值

        >>> wind_feature(code='(S2707241 + S2707194)/2')
                        (S2707241 + S2707194)/2
            2019-03-31           363.050
            2019-06-30           361.000
            2019-09-30           360.165
            2019-12-31           373.205

        4. 获取上海优质写字楼租金，并以长型数据框输出，同样适用于复合指标

        >>> wind_feature(code='S2707241', output='long')
                code        date      value
            0  S2707241  2019-03-31  298.90
            1  S2707241  2019-06-30  296.80
            2  S2707241  2019-09-30  293.83
            3  S2707241  2019-12-31  318.81
    """

    if not w.isconnected():
        w.start()

    if isinstance(code, list):
        if len(code) > 1:
            raise ValueError('max length of code should be one.')
        else:
            code = code[0]

    if not start_date:
        start_date = str(pd.to_datetime(dt.datetime.today().year - 1, format='%Y').date())

    codes = filter_codes(code)
    edb_res = w.edb(codes, startDate=start_date, endDate=end_date)

    if len(edb_res.Codes) > 1 & len(edb_res.Data) == 1:
        result = edb_res.Data
    else:
        result = list(map(list, zip(*edb_res.Data)))
        
    data = pd.DataFrame(result, columns=edb_res.Codes)
    data.index = edb_res.Times

    data.loc[:, code] = data.eval(code)
    
    if not keep:
        data = data.filter([code])
    
    if output == 'long':
        data = data.unstack().reset_index()
        data.columns = ['code', 'date', 'value']

    return data
	
def filter_codes(code):
    """ 从复合指标提取指标 ID

    Args:
        code: 需要提取 wind 指标 ID 的复合指标

    Returns:
        list: 复合指标中包括的指标 ID（字母开头）

    Examples:
        1. 复合指标提取

        >>> filter_codes(code='(S2707241 + S2707241)/2')
            ['S2707241', 'S2707241']
    """
    clean_codes = list(filter(None, re.split("([+-/*()])", code.replace(" ", ""))))
    return [item for item in list(filter(None, clean_codes)) if item[0].isalpha()]
	


def wind_edb(codes, start_date=None, end_date=None, output='wide'):
    """ 从 wind 获取数据

    本函数为方便从 wind 取出单个指标或者多个指标的数据，指标可以为复合指标，也即通过单指标通过加减乘除得到，输出数据可选为长型或者宽型数据输出。

    Args:
        codes (str or list): （复合）指标 ID 或其构成的列表
        start_date (str): 数据开始时间，默认为去年 1 月 1 日
        end_date (str): 数据结束时间，默认为 None
        output: 返回的数据类型，如果是 `wide`，则返回 wind 默认 edb 函数的结果

    Returns:
        dataframe: 宽型或者长型的数据

    Examples:

        1. 获取特定时间点开始单个指标的数据

        >>> wind_edb(codes='S2707241')
                         S2707241
            2019-03-31    298.90
            2019-06-30    296.80
            2019-09-30    293.83
            2019-12-31    318.81

        2. 获取特定时间区间内的数据

        >>> wind_edb(codes='S2707241', start_date='2019-01-01', end_date='2019-06-30')
                         S2707241
            2019-03-31    298.90
            2019-06-30    296.80

        3. 获取多个指标的数据，并合并输出为宽型

        >>> wind_edb(codes=['S2707241', 'S2707194'])
                         S2707241  S2707194
            2019-03-31    298.90     427.2
            2019-06-30    296.80     425.2
            2019-09-30    293.83     426.5
            2019-12-31    318.81     427.6

        4. 获取多个指标的数据，合并输出为长型

        >>> wind_edb(codes=['S2707241', 'S2707194'], output='long')
                code        date       value
            0  S2707241  2019-03-31  298.90
            1  S2707241  2019-06-30  296.80
            2  S2707241  2019-09-30  293.83
            3  S2707241  2019-12-31  318.81
            4  S2707194  2019-03-31  427.20
            5  S2707194  2019-06-30  425.20
            6  S2707194  2019-09-30  426.50
            7  S2707194  2019-12-31  427.60

        5. 获取多个指标的数据，合并输出为长型

        >>> wind_edb(codes=['S2707241', 'S2707194', 'S2707241 + S2707194'])
                         S2707241  S2707194  S2707241 + S2707194
            2019-03-31    298.90     427.2       726.10
            2019-06-30    296.80     425.2       722.00
            2019-09-30    293.83     426.5       720.33
            2019-12-31    318.81     427.6       746.41
    """
    if isinstance(codes, str):
        codes = [codes]
    data = pd.DataFrame()
    for code in codes:
        ticker_data = wind_feature(code=code, start_date=start_date, end_date=end_date, output=output)
        if output == 'wide':
            if data.shape[0]:
                data = data.merge(ticker_data, how='outer', left_index=True, right_index=True)
            else:
                data = ticker_data
        else:
            data = pd.concat([data, ticker_data]).reset_index(drop=True)

    return data


def parse_index(indicator_file, clean=False, lang='en'):
    """ 解析从 wind 导出的指标信息

    Args:
        indicator_file (str): 指标文件
        clean (bool): 是否经过处理过的，如果转置过，则为 True
        lang (str): 输出指标表的列名为英文（`lang='en'`）或者中文

    Returns:
        dataframe: 清理干净的指标表，用于存入指标库
    """
    if not clean:
        data = pd.read_excel(indicator_file, header=None, nrows=9)
        col_names = data.iloc[:, 0].tolist()
        result = data.iloc[:, 1:].transpose()
        result.columns = col_names
    else:
        result = pd.read_excel(indicator_file, header=0)

    result['省'], result['市'], result['指标'] = zip(*result['指标名称'].apply(parse_indicator))
    result = result.filter(['指标', '指标ID', '频率', '单位', '省', '市', '来源'])

    if lang == 'en':
        result.columns = ['indicator', 'code', 'frequency', 'unit', 'province', 'city', 'source']

    return result


def indicator_data(indicators_table, indicator, start_date):
    """ 从指标表中提取某个指标的数据

    Args:
        indicators_table (dataframe): 指标表
        indicator (str): 特定指标
        start_date (str): 数据开始时间

    Returns:
        dataframe: 特定指标从 `start_date` 的数据
    """
    indicator_table = indicators_table.query('indicator == "%s"' % indicator).reset_index(drop=True)
    indicator_table['codex'] = indicator_table[['province', 'city', 'indicator']].apply(lambda x: ':'.join(x), axis=1)
    indicator_dict = dict(zip(indicator_table['code'], indicator_table['codex']))
    codes = [*indicator_dict]
    data = wind_edb(codes=codes, start_date=start_date, output='wide')
    data.columns = [indicator_dict[code] for code in codes]
    return data

def parse_indicator(indicator):
    """ 解析 wind 指标名

    此函数主要为解析 wind 中指标名，提取其中的省份、城市以及真实指标名。

    Args:
        indicator (str): 需要提取的 wind 指标名

    Returns:
        tuple:
            - **province** (*str*): 省份/None
            - **city** (*str*): 城市/None
            - **indicator** (*str*): 清洗之后的指标名

    Examples:
        1. 只包含省份

        >>> parse_indicator('江苏:城镇居民人均可支配收入:同比')
            ('江苏', None, '城镇居民人均可支配收入:同比')

        2. 直辖市

        >>> parse_indicator('城镇居民人均可支配收入:上海:同比')
            ('上海', '上海', '城镇居民人均可支配收入:同比')

        3. 包括省份和城市

        >>> parse_indicator('江苏:苏州:城镇居民人均可支配收入:同比')
            ('江苏', '苏州', '城镇居民人均可支配收入:同比')

        4. 指标中仅包括城市名

        >>> parse_indicator('苏州:城镇居民人均可支配收入:同比')
            ('江苏', '苏州', '城镇居民人均可支配收入:同比')

        5. 省份、城市均没有

        >>> parse_indicator('城镇居民人均可支配收入:同比')
            ('None', 'None', '城镇居民人均可支配收入:同比')

    """
    nodes = indicator.split(':')
    pid, province = iv_loc(nodes, list(city_map.keys()))

    # get the index and value of city
    target_city = city_map[province] if province else dict_values(city_map)
    cid, city = iv_loc(nodes, target_city)

    # remove province and city from wind indicator
    if province:
        nodes.remove(province)

    if city:
        if province != city:
            nodes.remove(city)
        if not province:
            province = return_key(city, city_map)

    clean_indic = ":".join(nodes)

    return province, city, clean_indic

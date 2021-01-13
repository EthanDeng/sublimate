import re
import itertools


def extract_numbers(source, first=True):
    num_list = [int(s) for s in re.findall(r'\d+', source)]
    if num_list:
        res = num_list[0] if first else num_list
        return res
    else:
        return None

def dict_values(query_dict):
    """ 将字典的值转为一个列表

    Args:
        query_dict (dict): 需要转换的字典，值也可以为列表。

    Returns:
        value_list: 字典值的值合并为列表

    Examples:

        1. 标准字典

        >>> city_dict = {
        ... '海南': '海口',
        ... '云南': '临沧'}
        >>> dict_values(city_dict)
            ['海口', '临沧']

        2. 字典值为列表

        >>> city_dict = {
        ... '海南': ['海口', '三亚', '三沙', '儋州'],
        ... '云南': ['昆明', '临沧', '丽江']}
        >>> dict_values(city_dict)
            ['海口', '三亚', '三沙', '儋州', '昆明', '临沧', '丽江']
    """
    value_list = list(query_dict.values())
    if isinstance([list(query_dict)[0]], list):
        return list(itertools.chain(*value_list))
    else:
        return value_list


def iv_loc(query_space, query_entry):
    """ 返回用户列表中所在的索引以及对应值

    此函数用于返回用户列表中元素在另外一个列表中的位置以及对应的值。

    Args:
        query_space (list): 用户列表
        query_entry (list): 需要查找的列表

    Returns:
        tuple:
            - **index** (*int*): 对应的位置索引
            - **value** (*str*): 对应的值

    Examples:
        1. 从用户列表中提取出 '湖北' 所在的位置以及对应的值

        >>> query_space = ['城镇居民人均可支配收入', '湖北', '武汉', '同比']
        >>> query_entry = ['江西', '安徽', '河南', '福建', '湖北', '广东']
        >>> index, value = iv_loc(query_space, query_entry)
        >>> index, value
            (1, '湖北')
        >>> query_space[index]
            '湖北'
    """
    match_result = [item in query_entry for item in query_space]
    position_index = [index for index, value in enumerate(match_result) if value]
    if position_index:
        index, value = position_index[0], query_space[position_index[0]]
    else:
        index, value = None, None
    return index, value


def return_key(query, query_dict):
    """ 返回值在字典中对应的键

    Args:
        query (str): 需要查找的值
        query_dict (dict): 需要查找的字典

    Returns:
        str: 值在字典中对应的键值，如果不存在，则不返回

    Examples:
        1. 当字典中的值长度为 1 时

        >>> city_map = {
        ... '海南': '海口',
        ... '云南': '临沧'}
        >>> return_key('丽江', city_map)
            '云南'

        2. 当字典中的值为列表时

        >>> city_map = {
        ... '海南': ['海口', '三亚', '三沙', '儋州市'],
        ... '云南': ['昆明', '曲靖', '丽江', '玉溪', '昭通', '保山', '普洱', '临沧']}
        >>> return_key('丽江', city_map)
            ’云南‘
    """

    for key, value in query_dict.items():
        if query in value:
            return key


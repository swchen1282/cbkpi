import os
import pandas as pd
import re


def count_parklots(trans_no: pd.Series) -> int:
    """
    Calculate all parking lots.
    :param trans_no: Column transaction pen number
    :return: number of all parking lots
    """
    var = [int(x[-1:]) for x in trans_no.values]
    return sum(var)


def floor_mapper(floor_str: str) -> int:
    """
    Extract each element of chinese string and map it into integer (SOME BUG HERE)
    :param floor_str: total floor in chinese string
    :return:
    """
    mapping_table = {
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10,
    }
    if floor_str and floor_str[-1] not in ('一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '層', '下'):
        return int(floor_str)  # '二十六' 沒有層
    elif len(floor_str) == 1:
        return mapping_table.get(floor_str)
    elif len(floor_str) == 2 and floor_str not in ('地下'):
        return 10 + mapping_table.get(floor_str[-1:])
    elif len(floor_str) == 3:
        return mapping_table.get(floor_str[0]) * 10 + mapping_table.get(floor_str[-1:])
    else:
        return 0


def total_floor_to_int(floor: pd.Series) -> list:
    """
    Transfer chinese words to integer (SOME BUG HERE)
    :param floor: pd.Series column of total_floor in chinese words
    :return: list of total_floor integer
    """
    floor_list = [x[:x.index('層')] if re.search('層', x) else x for x in floor.values]  # use index to get the stop position
    result = [floor_mapper(x) for x in floor_list]
    return result


def data_processor():
    absolute_path = os.path.dirname(__file__)
    data_source_path = os.path.dirname(os.path.dirname(absolute_path))
    os.chdir(os.path.join(data_source_path, 'data_storage'))
    df_all = pd.read_csv('df_all.csv')
    print(df_all)

    # change total_floor_number from string to number
    df_all['total floor number'] = df_all['total floor number'].fillna('層')
    df_all['total_floor_number_int'] = total_floor_to_int(df_all['total floor number'])

    # filter_a
    filter_a = df_all[
        (df_all['main use'] == '住家用') &
        (df_all['building state'].str.contains('住宅大樓')) &
        (df_all['total_floor_number_int'] >= 13)
    ]
    filter_a.to_csv('filter_a.csv', index=False)

    # filter_b
    result = {
        'total_cases': len(df_all),
        'total_parklots': count_parklots(df_all['transaction pen number']),
        'mean_tot_price': pd.to_numeric(df_all['total price NTD']).mean(),
        'mean_park_tot_price': pd.to_numeric(df_all['the berth total price NTD']).mean()
    }

    filter_b = pd.DataFrame(result.values(), index=result.keys())
    filter_b.to_csv('filter_b.csv', index=False)


if __name__ == '__main__':
    data_processor()

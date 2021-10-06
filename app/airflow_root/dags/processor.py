import pandas as pd


def count_parklots(trans_no: pd.Series) -> int:
    """
    Calculate all parking lots.
    :param trans_no: Column transaction pen number
    :return: number of all parking lots
    """
    var = [int(x[-1:]) for x in trans_no.values]
    return sum(var)


def mapper(floor_str: str) -> int:
    """
    Extract each element of chinese string and map it into integer
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
    if len(floor_str) == 1:
        return mapping_table.get(floor_str)
    elif len(floor_str) == 2:
        return 10 + mapping_table.get(floor_str[-1:])
    elif len(floor_str) == 3:
        return mapping_table.get(floor_str[0]) * 10 + mapping_table.get(floor_str[-1:])
    else:
        return 0


def total_floor_to_int(floor: pd.Series) -> list:
    """
    Transfer chinese words to integer
    :param floor: pd.Series column of total_floor in chinese words
    :return: list of total_floor integer
    """
    floor_list = [x[:x.index('層')] for x in floor.values]  # use index to get the stop position
    result = [mapper(x) for x in floor_list]
    return result


def main():
    # read data, remove first row and add Column: City, concatenate it
    df_a = pd.read_csv('./quiz1/data_source/a_lvr_land_a.csv').iloc[1:, :].assign(城市='Taipei')
    df_b = pd.read_csv('./quiz1/data_source/b_lvr_land_a.csv').iloc[1:, :].assign(城市='Taichung')
    df_e = pd.read_csv('./quiz1/data_source/e_lvr_land_a.csv').iloc[1:, :].assign(城市='Kaohsiung')
    df_f = pd.read_csv('./quiz1/data_source/f_lvr_land_a.csv').iloc[1:, :].assign(城市='Newtaipei')
    df_h = pd.read_csv('./quiz1/data_source/h_lvr_land_a.csv').iloc[1:, :].assign(城市='Taoyuan')
    df_all = pd.concat([df_a, df_b, df_e, df_f, df_h], axis=0)

    # change total_floor_number from string to number
    df_all['總樓層數'] = df_all['總樓層數'].fillna('層')
    df_all['總樓層數_數字'] = total_floor_to_int(df_all['總樓層數'])

    # filter_a
    filter_a = df_all.query('主要用途 == "住家用" and 建物型態.str.contains("住宅大樓") and 總樓層數_數字 >= 13', engine='python')
    filter_a.to_csv('./quiz1/output/filter_a.csv')

    # filter_b
    result = {
        'total_cases': len(df_all),
        'total_parklots': count_parklots(df_all['交易筆棟數']),
        'mean_tot_price': pd.to_numeric(df_all['總價元']).mean(),
        'mean_park_tot_price': pd.to_numeric(df_all['車位總價元']).mean()
    }

    filter_b = pd.DataFrame(result.values(), index=result.keys())
    filter_b.to_csv('./quiz1/output/filter_b.csv')


if __name__ == '__main__':
    print('----------start------------')
    main()
    print('----------end------------')

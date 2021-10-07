import os
import pandas as pd
import re


def data_reader():
    absolute_path = os.path.dirname(__file__)
    data_source_path = os.path.dirname(os.path.dirname(absolute_path))
    os.chdir(os.path.join(data_source_path, 'data_source'))
    dir_list = os.listdir()
    dir_list.sort()

    print(f"absolute_path={absolute_path}")
    print(f"data_source_path={data_source_path}")
    print(dir_list)
    print(f"current path is: {os.getcwd()}; start data processing")

    result = pd.DataFrame()
    # dir_list = ['109S1', '109S2', '109S3', '109S4']  # test
    for i in range(len(dir_list)):
        temp_folder = dir_list[i]
        temp_path = os.path.join(os.getcwd(), temp_folder)
        if re.search(r'.zip', temp_folder):
            print(f"{temp_folder} is a zip file, skip")
        else:
            csv_list = os.listdir(temp_path)
            target_list = [x for x in csv_list if re.search('(^[afe].*_a.csv)|(^[hb].*_b.csv)', x) is not None]
            for csv in target_list:
                data_type = csv[-5].upper()
                df_name = f"{re.sub('S', '_', temp_folder)}_{csv[0].upper()}_{data_type}"
                data = pd.read_csv(os.path.join(temp_path, csv))
                data = data.set_axis(list(data.iloc[0, ]), axis=1).iloc[1:, ]  # use second row as new column names, and remove it
                data['df_name'] = df_name
                result = result.append(data)
                print(f"import {df_name} data into pd.DataFrame successfully")
    result.to_csv(data_source_path + '/data_storage/df_all.csv', index=False)
    return 'successfully'


# def main():
#     # move to cbkpi/app/datasource
#     absolute_path = os.path.dirname(__file__)
#     data_source_path = os.path.dirname(os.path.dirname(absolute_path))
#     os.chdir(os.path.join(data_source_path, 'data_source'))
#     print(os.listdir())
#     print(f"current path is: {os.getcwd()}; start data processing")
#
#     # find target:
#     # 臺北市/新北市/高雄市: a/f/e_*_a
#     data = data_reader()
#     print(data)
#     # 桃園市/臺中市: h/b_*_b
#
#     # get folder name
#
#     # column modify
#     # second row as column name
#     # add new column: df_name=<year>_<season>_<ciry>_<AorB>
#
#     # value modify
#
#     # read data, remove first row and add Column: City, concatenate it
#     df_a = pd.read_csv('./quiz1/data_source/a_lvr_land_a.csv').iloc[1:, :].assign(城市='Taipei')
#     df_b = pd.read_csv('./quiz1/data_source/b_lvr_land_a.csv').iloc[1:, :].assign(城市='Taichung')
#     df_e = pd.read_csv('./quiz1/data_source/e_lvr_land_a.csv').iloc[1:, :].assign(城市='Kaohsiung')
#     df_f = pd.read_csv('./quiz1/data_source/f_lvr_land_a.csv').iloc[1:, :].assign(城市='Newtaipei')
#     df_h = pd.read_csv('./quiz1/data_source/h_lvr_land_a.csv').iloc[1:, :].assign(城市='Taoyuan')
#     df_all = pd.concat([df_a, df_b, df_e, df_f, df_h], axis=0)
#
#     # change total_floor_number from string to number
#     df_all['總樓層數'] = df_all['總樓層數'].fillna('層')
#     df_all['總樓層數_數字'] = total_floor_to_int(df_all['總樓層數'])
#
#     # filter_a
#     filter_a = df_all.query('主要用途 == "住家用" and 建物型態.str.contains("住宅大樓") and 總樓層數_數字 >= 13', engine='python')
#     filter_a.to_csv('./quiz1/output/filter_a.csv')
#
#     # filter_b
#     result = {
#         'total_cases': len(df_all),
#         'total_parklots': count_parklots(df_all['交易筆棟數']),
#         'mean_tot_price': pd.to_numeric(df_all['總價元']).mean(),
#         'mean_park_tot_price': pd.to_numeric(df_all['車位總價元']).mean()
#     }
#
#     filter_b = pd.DataFrame(result.values(), index=result.keys())
#     filter_b.to_csv('./quiz1/output/filter_b.csv')
#
#
if __name__ == '__main__':
    print('----------start------------')
    data_reader()
    print('----------end------------')

# Ref: https://www.finlab.tw/real-estate-analysis1/
import logging
from datetime import timedelta, datetime
from airflow import DAG  # The DAG object; we'll need this to instantiate a DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator  # Operators; we need this to operate!
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.utils.email import send_email
import configparser
import os
import requests
import zipfile
import time
import multiprocessing as mp
logger = logging.getLogger('my_logger')
absolute_path = os.path.dirname(__file__)
data_source_path = os.path.dirname(os.path.dirname(absolute_path))


def crawler(params: list) -> str:
    """
    use map function to concurrently crawl the data

    :param params: list of dictionary, keys: ['year', 'list']
    :return:
    """
    try:
        year = params['year']
        season = params['season']
        if year > 1000:
            year -= 1911

        # download real estate zip file
        logger.info(f"start to crawl zip file: {str(year)}S{str(season)}")
        res = requests.get("https://plvr.land.moi.gov.tw//DownloadSeason?season=" + str(year) + "S" + str(
            season) + "&type=zip&fileName=lvr_landcsv.zip")  # url: /DownloadSeason?season="+season+"&type=zip&fileName=lvr_land"+fileFormat+".zip"

        # save content to zip file and extract it
        if not os.path.isdir(os.path.join(data_source_path, 'data_source')):
            os.mkdir(os.path.join(data_source_path, 'data_source'))
        os.chdir(os.path.join(data_source_path, 'data_source'))
        file_name = f"{str(year)}S{str(season)}.zip"
        with open(file_name, 'wb') as fn:
            fn.write(res.content)

        # extract zip into new folder
        data_folder = os.path.join(data_source_path, 'data_source', f"{str(year)}S{str(season)}")
        if not os.path.isdir(data_folder):
            os.mkdir(data_folder)
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(data_folder)
        logger.info(f"craw and extract {str(year)}S{str(season)} data successfully.")
        time.sleep(1)
        return 'Hello'
    except Exception as e:
        raise logger.exception(e)


if __name__ == '__main__':
    param_crawl = [
        {'year': 106, 'season': 1}, {'year': 106, 'season': 2}, {'year': 106, 'season': 3}, {'year': 106, 'season': 4},
        {'year': 107, 'season': 1}, {'year': 107, 'season': 2}, {'year': 107, 'season': 3}, {'year': 107, 'season': 4},
        {'year': 108, 'season': 1}, {'year': 108, 'season': 2}, {'year': 108, 'season': 3}, {'year': 108, 'season': 4},
        {'year': 109, 'season': 1}, {'year': 109, 'season': 2}, {'year': 109, 'season': 3}, {'year': 109, 'season': 4},
    ]

    # for dev
    pool = mp.Pool()
    myo = pool.map(crawler, param_crawl)
    print(list(myo))

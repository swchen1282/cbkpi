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
from data_crawler import crawler
from data_reader import data_reader
from data_processor import data_processor
default_args = {
    'owner': 'swc',
    'depends_on_past': False,
    'email': ['swchen1282@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(hours=12),
}


with DAG(
    dag_id='estate_pipeline',
    default_args=default_args,
    description='Craw real estate data into local and process',
    start_date=datetime(2021, 10, 10, 0, 0, 0),
    schedule_interval=timedelta(hours=12),
) as dag:
    # param_crawl = [
    #     {'year': 106, 'season': 1}, {'year': 106, 'season': 2}, {'year': 106, 'season': 3}, {'year': 106, 'season': 4},
    #     {'year': 107, 'season': 1}, {'year': 107, 'season': 2}, {'year': 107, 'season': 3}, {'year': 107, 'season': 4},
    #     {'year': 108, 'season': 1}, {'year': 108, 'season': 2}, {'year': 108, 'season': 3}, {'year': 108, 'season': 4},
    #     {'year': 109, 'season': 1}, {'year': 109, 'season': 2}, {'year': 109, 'season': 3}, {'year': 109, 'season': 4},
    # ]

    # task name should name like but not as same as task_id and python_callable for convenient
    # etl = BranchPythonOperator(
    #     task_id='etl',
    #     python_callable=etl_decider,
    #     provide_context=True,
    # )
    # crawl = PythonOperator(
    #     task_id='crawl_the_data',
    #     op_args=[param_crawl],
    #     python_callable=crawler,
    # )
    # stop = DummyOperator(task_id='stop')
    # generate_mail = PythonOperator(
    #     task_id='start_ETL',
    #     python_callable=generate_mail_message,
    #     provide_context=True,
    # )
    # mailer = EmailOperator(
    #     task_id='send_email',
    #     to=['swchen@kfsyscc.org'],
    #     subject=f"start ETL job on Airflow [門診申報抽檔]",
    #     html_content=f"init ETL jobs from ora to pg, ins_month={param['yyymm']}"
    # )

    #
    # pg_insert = PythonOperator(
    #     task_id='pg_inserter',
    #     python_callable=pg_inserter,
    #     op_kwargs={'param': param},
    #     on_success_callback=notify_email,
    #     on_failure_callback=notify_email,
    # )

    # define workflow
    # etl >> generate_mail >> mailer >> pg_insert
    # etl >> stop
    # crawl >> stop
    # stop

    data_reader = PythonOperator(
        task_id='data_reader',
        python_callable=data_reader
    )

    data_processor = PythonOperator(
        task_id='data_processor',
        python_callable=data_processor
    )

    data_reader >> data_processor

if '__name__' == '__main__':
    data_reader()
    # crawler(param_crawl[0])

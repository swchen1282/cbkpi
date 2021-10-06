import logging
from datetime import timedelta, datetime
from airflow import DAG  # The DAG object; we'll need this to instantiate a DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator  # Operators; we need this to operate!
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.utils.email import send_email
# from airflow.utils.dates import days_ago
import configparser
import os
# import pandas as pd
from sqlalchemy import create_engine, Integer, Column, String, Table, CLOB, DATE, Date, and_, func
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from src.database.models import Oinmast


default_args = {
    'owner': 'swc',
    'depends_on_past': False,
    'email': ['swchen1282@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 4,
    'retry_delay': timedelta(hours=1),
    'schedule_interval': '@daily',
}


def get_ora_engine():
    config = configparser.ConfigParser()
    config.read(os.environ['ORACONF'], encoding='UTF-8')
    conf = config['PRODUCTION']
    user = conf['user']
    password = conf['password']
    dsn = conf['dsn']
    port = conf['port']
    db_name = conf['db_name']

    ora_engine = create_engine(
        f"oracle+cx_oracle://{user}:{password}@{dsn}:{port}/?service_name={db_name}", pool_size=8, echo=False
    )
    engine_base = declarative_base()  # init sqlalchemy connect engine base
    engine_base.metadata.bind = ora_engine
    engine_base.metadata.schema = 'KFSYSCC'  # need to change back when query inqgen, watchout caps
    return ora_engine


def check_oracle(param):
    ora_con = get_ora_engine()
    oinmast = ora_con.execute(
        """ SELECT * FROM OINMAST WHERE INS_MONTH = :yyymm """,
        dict((k, v) for k, v in param.items() if k == 'yyymm')  # filter dictionary by keys
    ).fetchone()
    if oinmast and len(oinmast) > 0:
        return 'yes_start_ETL'
    else:
        return 'no_skip'


def etl_decider(**context):
    msg = context['task_instance'].xcom_pull(task_ids='check_oracle')  # result of check_oracle
    if msg == 'yes_start_ETL':
        return 'start_ETL'
    else:
        return 'stop_ETL'


def generate_mail_message(**context):
    msg = context['task_instance'].xcom_pull(task_ids='etl')  # result of check_oracle
    print('產生要透過 email 發送的訊息')


def get_pg_engine():
    pg_engine = create_engine('postgresql://postgres:pg1234@localhost:5678/pgdb', pool_size=8, echo=False)  # True: INFO, False: ERROR
    pg_Base = declarative_base()
    pg_Base.metadata.bind = pg_engine
    # pg_Base.metadata.schema = 'kfsyscc'
    return pg_engine


def pg_inserter(param):
    # oracle config
    ora_engine = get_ora_engine()
    ora_base = declarative_base()
    ora_base.metadata.bind = ora_engine
    ora_base.metadata.schema = 'KFSYSCC'

    ora_oinmast = ora_engine.execute(
        """ select * from oinmast where ins_month = :yyymm """,
        dict((k, v) for k, v in param.items() if k == 'yyymm')
    ).fetchall()  # sqlalchemy ResultProxy object
    ora_oinmast = [dict(zip(x.keys(), x)) for x in ora_oinmast]  # use .keys() to get column name(keys) of sqlalchemy ResultProxy object

    ora_oinord = ora_engine.execute(
        """ select * from oinord where ins_month = :yyymm""",
        dict((k, v) for k, v in param.items() if k == 'yyymm')
    ).fetchall()
    ora_oinord = [dict(zip(x.keys(), x)) for x in ora_oinord]

    ora_oinacc = ora_engine.execute(
        """ select * from oinacc where ins_month = :yyymm""",
        dict((k, v) for k, v in param.items() if k == 'yyymm')
    ).fetchall()
    ora_oinacc = [dict(zip(x.keys(), x)) for x in ora_oinacc]

    # pg config
    pg_engine = get_pg_engine()
    pg_base = declarative_base()
    pg_base.metadata.bind = pg_engine
    pg_base.metadata.schema = 'kfsyscc'

    # you need to create schema first on other airflow DAG
    pg_oinmast = Table('oinmast', pg_base.metadata, autoload=True)  # 先用 reflect 全拿，後續可調整為只拿需要的就好
    pg_oinord = Table('oinord', pg_base.metadata, autoload=True)
    pg_oinacc = Table('oinacc', pg_base.metadata, autoload=True)
    # pg_session = sessionmaker(bind=pg_engine)

    with pg_engine.connect() as conn:
        conn.execute(pg_oinmast.insert(), ora_oinmast)
        print(f"insert into kfsyscc.oinmast@pg successfully; rows={len(ora_oinmast)}")
    with pg_engine.connect() as conn:
        conn.execute(pg_oinord.insert(), ora_oinord)
        print(f"insert into kfsyscc.oinord@pg successfully; rows={len(ora_oinord)}")
    with pg_engine.connect() as conn:
        conn.execute(pg_oinacc.insert(), ora_oinacc)
        print(f"insert into kfsyscc.oinacc@pg successfully; rows={len(ora_oinacc)}")


def notify_email(context, **kwargs):
    """
        Send custom email alerts.
        For details of develope this function please check: https://bhavaniravi.com/blog/sending-emails-from-airflow/
        For details of context['ti'], please check source below:
            https://github.com/apache/airflow/blob/4f20f607764bb3477419321b5dfd0c53ba1db3c0/airflow/models.py#L1523
    """
    config = configparser.ConfigParser()
    config.read(os.environ['AIRFLOW_HOME'] + '/airflow.cfg', encoding='UTF-8')
    conf = config['webserver']
    ti = context['ti']
    if ti.current_state() == 'FAILURE':
        status = 'FAIL'
    else:
        status = 'SUCCESS'
    logs_link = f"{conf['base_url']}/log?task_id={ti.task_id}&dag_id={ti.dag_id}&execution_date={ti.execution_date}"
    email_title = f"[{status}] Airflow Task {ti.task_id}"
    email_body = f"task {ti.task_id} in DAG {ti.dag_id} [{status}], please check log below: <br> {logs_link}"
    send_email('swchen@kfsyscc.org', email_title, email_body)


with DAG(
    'ora2pg_ETL_v1',
    default_args=default_args,
    description='check data in oracle.oinmast/oinord/oinacc; if yes, transport data from oracle to pg container',
    start_date=datetime(2021, 5, 5, 22, 0, 0),
    schedule_interval=timedelta(days=1),
) as dag:
    param = {
        'now': datetime.strftime(datetime.now(), '%Y%m%d'),
        'yyymm': str(int(datetime.strftime(datetime.now(), '%Y%m%d')[0:4]) - 1911) +
                 datetime.strftime(datetime.now(), '%Y%m%d')[4:6],
        'yyyymm': datetime.strftime(datetime.now(), '%Y%m%d')[0:4] + datetime.strftime(datetime.now(), '%Y%m%d')[4:6]
    }

    # task name should name like but not as same as task_id and python_callable for convenient
    check_ora = PythonOperator(
        task_id='check_oracle',
        python_callable=check_oracle,
        op_kwargs={'param': param},
        on_success_callback=notify_email,
        on_failure_callback=notify_email,
    )
    etl = BranchPythonOperator(
        task_id='etl',
        python_callable=etl_decider,
        provide_context=True,
    )
    generate_mail = PythonOperator(
        task_id='start_ETL',
        python_callable=generate_mail_message,
        provide_context=True,
    )
    mailer = EmailOperator(
        task_id='send_email',
        to=['swchen@kfsyscc.org'],
        subject=f"start ETL job on Airflow [門診申報抽檔]",
        html_content=f"init ETL jobs from ora to pg, ins_month={param['yyymm']}"
    )
    stop = DummyOperator(task_id='stop_ETL')

    pg_insert = PythonOperator(
        task_id='pg_inserter',
        python_callable=pg_inserter,
        op_kwargs={'param': param},
        on_success_callback=notify_email,
        on_failure_callback=notify_email,
    )

    # define workflow
    check_ora >> etl

    etl >> generate_mail >> mailer >> pg_insert
    etl >> stop


if __name__ == '__main__':
    date_p = {
        'now': datetime.strftime(datetime.now(), '%Y%m%d'),
        'yyymm': str(int(datetime.strftime(datetime.now(), '%Y%m%d')[0:4]) - 1911) +
                 datetime.strftime(datetime.now(), '%Y%m%d')[4:6],
        'yyyymm': datetime.strftime(datetime.now(), '%Y%m%d')[0:4] + datetime.strftime(datetime.now(), '%Y%m%d')[4:6]
    }

    # for dev
    check_oracle(date_p)
    pg_inserter(date_p)
    notify_email(dag)

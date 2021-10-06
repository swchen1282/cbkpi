## Add ENV (./venv/bin/activate)
```
# add PYTHONPATH
export PYTHONPATH=$(pwd)

# add airflow root dir on 
export AIRFLOW_HOME=$(pwd)/airflow_root
```

## Activate airflow
```
# install airflow 2.0.1
pip install apache-airflow

# activate airflow db (airflow==2.0.1)
airflow db init

# create user
airflow users create -e swchen1282@gmail.com -f admin -l admin -r Admin -u admin -p 123456

# activate webserver
airflow webserver -p 8081 (default is 8080)

# activate scheduler
airflow scheduler
```

### setting configs (($AIRFLOW_HOME)/airflow.cfg)

- change `load_examples = False` inside `airflow.cfg` and use command `airflow db reset`
- or set AIRFLOW__CORE__LOAD_EXAMPLES: 'false' in `docker-compose.yml`
- 

### mail server (smtp)

```yml
default:
  email_delivery:
    delivery_method: :smtp
    smtp_settings:
      address: '<mail>@host.com'
      port: 25
```

## test task is ok or not
`airflow tasks test <dag_name> <task_id> <yyyy-mm-dd>` e.g.: airflow tasks test ora2pg_ETL_v1 etl 2021-04-21
echo 'start to set PYTHONPATH and AIRFLOW_HOME'
export PYTHONPATH=$(pwd)/app
export AIRFLOW_HOME=$(pwd)/app/airflow_root
set | grep PYTHONPATH
set | grep AIRFLOW_HOME


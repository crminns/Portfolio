## This is a DAG designed to extract data from several different types of files then
## transform and merge the data into one CSV file. This is done by defining the various tasks
## required, then creating a data pipeline using these tasks.

# import libraries
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# define DAG arguments

default_args = {
    'owner' : 'Cody Minns',
    'start_date' : days_ago(0),
    'email' : 'crminns@gmail.com',
    'email_on_failure' : True,
    'email_on_retry' : True,
    'retries' : 1,
    'retry_delay' : timedelta(minutes = 5)
}

# define DAG

dag = DAG(
    'ETL_toll_data',
    schedule_interval = timedelta(days = 1),
    default_args = default_args,
    description = 'ETL pipeline for toll data from various sources'
)

# define the unzip data task

unzip_data = BashOperator(
    task_id = 'unzip_data',
    bash_command = 'tar -zxvf /$AIRFLOW_HOME/../data/tolldata.tgz -C /$AIRFLOW_HOME/../data/',
    dag = dag
)

# define the extract from csv task

extract_data_from_csv = BashOperator(
    task_id = 'extract_data_from_csv',
    bash_command = 'cut -d"," -f1-4 /$AIRFLOW_HOME/../data/vehicle-data.csv > /$AIRFLOW_HOME/../data/csv_data.csv',
    dag = dag
)

# define the extract from tsv task

extract_data_from_tsv = BashOperator(
    task_id = 'extract_data_from_tsv',
    bash_command = 'cut -f5-7 /$AIRFLOW_HOME/../data/tollplaza-data.tsv | tr "\t" ","  > /$AIRFLOW_HOME/../data/tsv_data.csv',
    dag = dag
)

# define the extract from fixed width task

extract_data_from_fixed_width = BashOperator(
    task_id = 'extract_data_from_fixed_width',
    bash_command = 'cut -b59-66 /$AIRFLOW_HOME/../data/payment-data.txt | tr " " "," > /$AIRFLOW_HOME/../data/fixed_width_data.csv',
    dag = dag
)

# define the consolidate data task

consolidate_data = BashOperator(
    task_id = 'consolidate_data',
    bash_command = 'paste -d"," /$AIRFLOW_HOME/../data/csv_data.csv /$AIRFLOW_HOME/../data/tsv_data.csv /$AIRFLOW_HOME/../data/fixed_width_data.csv > /$AIRFLOW_HOME/../data/extracted_data.csv',
    dag = dag
)

# define the transform data task

transform_data = BashOperator(
    task_id = 'transform_data',
    bash_command = 'paste -d"," <(cut -d"," -f1-3 /$AIRFLOW_HOME/../data/extracted_data.csv) <(cut -d"," -f4 /$AIRFLOW_HOME/../data/extracted_data.csv | tr [:lower:] [:upper:]) <(cut -d"," -f5- /$AIRFLOW_HOME/../data/extracted_data.csv) > /$AIRFLOW_HOME/../data/transformed_data.csv',
    dag = dag
)

# define task pipeline

unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data

import os
os.chdir(r"C:\Users\crmin\OneDrive\Desktop\Professional & School Stuff\Job Stuff\ETL Example")

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
    'owner' : 'Fake McName',
    'start_date' : days_ago(0),
    'email' : 'mcname@fake.com',
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
    description = 'Apache Airflow Final Assignment'
)

# define the unzip data task

unzip_data = BashOperator(
    task_id = 'unzip_data',
    bash_command = 'tar -zxvf tolldata.tgz',
    dag = dag
)

# define the extract from csv task

extract_data_from_csv = BashOperator(
    task_id = 'extract_data_from_csv',
    bash_command = 'cut -d"," -f1-4 vehicle-data.csv > csv_data.csv',
    dag = dag
)

# define the extract from tsv task

extract_data_from_tsv = BashOperator(
    task_id = 'extract_data_from_tsv',
    bash_command = 'cut -f5-7 tollplaza-data.tsv | tr "\t" ","  > tsv_data.csv',
    dag = dag
)

# define the extract from fixed width task

extract_data_from_fixed_width = BashOperator(
    task_id = 'extract_data_from_fixed_width',
    bash_command = 'cut -b58-66 payment-data.txt | tr " " "," > fixed_width_data.csv',
    dag = dag
)

# define the consolidate data task

consolidate_data = BashOperator(
    task_id = 'consolidate_data',
    bash_command = 'paste csv_data.csv tsv_data.csv fixed_width_data.csv > extracted_data.csv',
    dag = dag
)

# define the transform data task

transform_data = BashOperator(
    task_id = 'transform_data',
    bash_command = 'paste <(cut -d"," -f1-3 extracted_data.csv) <(cut -d"," -f4 extracted_data.csv | tr ":lower:" ":upper:") \
                          <(cut -d"," -f5- extracted_data.csv) > Staging/transformed_data.csv',
    dag = dag
)

# define task pipeline

unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data
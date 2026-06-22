from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="flight_price_retraining",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mlops", "flight-price"],
) as dag:

    train_model = BashOperator(
        task_id="train_random_forest_model",
        bash_command="""
        cd /opt/airflow/project &&
        python train_model.py
        """
    )
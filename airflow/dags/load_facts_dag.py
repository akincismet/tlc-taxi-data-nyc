from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from datetime import datetime


@dag(
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dimension"],
    template_searchpath='/opt/airflow/dags/repo/airflow/dags/spark_on_k8s',
    is_paused_upon_creation=True
)
def load_facts_dag():
    ingest_task = SparkKubernetesOperator(task_id="load-facts",
        image="spark-load_facts:1.0",
        namespace="default",
        name="load_facts",
        application_file="load_facts_sparkApplication.yaml",

    )

    # Do NOT call ingest_task(), just let it be registered in the DAG
    # If you had more tasks, you'd define dependencies like: task1 >> task2


dag_instance = load_facts_dag()
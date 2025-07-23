from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging


def test_mongo_connection():
    try:
        client = MongoClient("mongodb://host.docker.internal:27017/", serverSelectionTimeoutMS=5000)
        # Intenta obtener información del servidor
        server_info = client.server_info()
        logging.info("✅ Conexión exitosa con MongoDB")
        logging.info("📋 Info del servidor:", server_info)
    except ConnectionFailure as e:
        logging.error("❌ Fallo en la conexión con MongoDB:", e)
        raise


with DAG(
    dag_id="test_mongo_connection",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["test", "mongo"],
) as dag:

    test_connection = PythonOperator(
        task_id="test_mongodb_connection",
        python_callable=test_mongo_connection,
    )

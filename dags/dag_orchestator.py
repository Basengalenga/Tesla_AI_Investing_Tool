from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
from extract_tesla import extraction_tesla
from extract_news import extraction_news
from extract_reddit import extraction_reddit
from raw_load import raw_load
from transform import transform
from gemini_driven_semantic_pipeline import gemini_analysis_pipeline
from gemini_driven_semantic_labeling import gemini_labeling
from aggregated_load import aggregated_load

# ----------------- DAG DEFINITION ---------------------

dag = DAG(
    'EPIC_ULTRA_SUPER_INTELIGENT_TESLA_VIGILANT',
    description='This ingestion DAG populates MongoDB WITH THE ULTIMATE TESLA DATA!!!!!!!!',
    start_date=datetime(2025, 7, 18),
    schedule_interval='@daily',
    catchup=False
)


# ----------------- TASK DEFINITIONS ---------------------



extract_tesla_task = PythonOperator(
    task_id="extract_tesla_task",
    python_callable=extraction_tesla,
    dag=dag
)

extract_news_task = PythonOperator(
    task_id="extract_news_task",
    python_callable=extraction_news,
    dag=dag
)

extract_reddit_task = PythonOperator(
    task_id="extract_reddit_task",
    python_callable=extraction_reddit,
    dag=dag
)

raw_load_task = PythonOperator(
    task_id="raw_load_task",
    python_callable=raw_load,
    dag=dag
)

transform_task = PythonOperator(
    task_id="transform_task",
    python_callable=transform,
    dag=dag
)

gemini_driven_semantic_pipeline_task = PythonOperator(
    task_id="gemini_driven_semantic_pipeline_task",
    python_callable=gemini_analysis_pipeline,
    dag=dag
)

gemini_driven_semantic_labeling_task = PythonOperator(
    task_id="gemini_driven_semantic_labeling_task",
    python_callable=gemini_labeling,
    dag=dag
)

aggregated_load_task = PythonOperator(
    task_id="aggregated_load_task",
    python_callable=aggregated_load,
    dag=dag
)


# ----------------- TASK DEPENDENCIES ---------------------

[extract_tesla_task, extract_news_task, extract_reddit_task] >> raw_load_task >> transform_task >> gemini_driven_semantic_labeling_task >> gemini_driven_semantic_pipeline_task >> aggregated_load_task


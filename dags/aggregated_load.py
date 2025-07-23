import pymongo
from pymongo import MongoClient
from datetime import datetime
import logging


def aggregated_load(ti):
    try:
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["projectUnit2"]
        collection = db["AggregatedData"]
    except Exception as e:
        logging.error(f"Couldn't connect to MongoDB --> {e}")
        return {"status": "error", "message": "Couldn't connect to MongoDB"}


    try:
        tesla_data = ti.xcom_pull(key="transformed_tesla", task_ids="transform_task")
        news_data = ti.xcom_pull(key="transformed_news", task_ids="transform_task")
        reddit_data = ti.xcom_pull(key="transformed_reddit", task_ids="transform_task")
        gemini_reddit_analysis = ti.xcom_pull(key="reddit_response", task_ids="gemini_driven_semantic_pipeline_task")
        gemini_news_analysis = ti.xcom_pull(key="news_response", task_ids="gemini_driven_semantic_pipeline_task")
        labeled_news = ti.xcom_pull(key="labeled_news", task_ids="gemini_driven_semantic_labeling_task")

        if tesla_data and news_data and reddit_data and gemini_news_analysis and gemini_reddit_analysis:
            aggregated_document = {
                "tesla_data": tesla_data,
                "news_data": news_data,
                "reddit_data": reddit_data,
                "gemini_reddit_analysis": gemini_reddit_analysis,
                "gemini_news_analysis": gemini_news_analysis,
                "labeled_news": labeled_news,
                "loaded_at": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
            collection.insert_one(aggregated_document)
            logging.info("Data successfully inserted into MongoDB")
            logging.info(f"Json uploaded: {aggregated_document}")
        else:
            logging.error("Missing data from XCom")
    except Exception as e:
        logging.error(f"Couldn't insert the data into MongoDB --> {e}")
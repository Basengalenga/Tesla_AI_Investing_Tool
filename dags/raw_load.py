import pymongo
from pymongo import MongoClient
from datetime import datetime
import logging

def raw_load(ti):
    try:
        client = MongoClient("mongodb://host.docker.internal:27017/")
        db = client["projectUnit2"]
        collection = db["RawData"]
    except Exception as e:
        logging.error(f"Couldn't connect to MongoDB --> {e}")
        return {"status": "error", "message": "Couldn't connect to MongoDB"}


    try:
        tesla_data = ti.xcom_pull(key="extracted_tesla", task_ids="extract_tesla_task")
        news_data = ti.xcom_pull(key="extracted_news", task_ids="extract_news_task")
        reddit_data = ti.xcom_pull(key="extracted_reddit", task_ids="extract_reddit_task")

        if tesla_data and news_data and reddit_data:
            raw_document = {
                "tesla_data": tesla_data,
                "news_data": news_data,
                "reddit_data": reddit_data,
                "loaded_at": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
            collection.insert_one(raw_document)
            logging.info("Data successfully inserted into MongoDB")
        else:
            logging.error("Missing data from XCom")
    except Exception as e:
        logging.error(f"Couldn't insert the data into MongoDB --> {e}")
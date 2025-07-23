import praw
import prawcore
import os
from dotenv import load_dotenv

def extraction_reddit(ti):

    load_dotenv()

    for var in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing required environment variable: {var}")
        
    reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')

    )
    try:
        subreddit = reddit.subreddit('investing')
        posts = list(subreddit.search('Tesla', limit=10, time_filter='week'))

        if not posts:
            ti.xcom_push(
                key="extracted_reddit",
                value={
                    "status": "empty",
                    "posts": []
                }
            )
        else:
            ti.xcom_push(
                key="extracted_reddit",
                value={
                    "status": "ok",
                    "posts": [{
                        "id": post.id,
                        "title": post.title,
                        "selftext": post.selftext,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created_utc": post.created_utc,
                        "url": post.url
                    } for post in posts]
                }
            )


    except prawcore.exceptions.ResponseException as e:
        error_msg = f"Failed to fetch data, Reddit API response error: {e}"
        ti.xcom_push(key="extracted_reddit", value={"error": error_msg})

    except Exception as e:
        error_msg = f"Unexpected error during data extraction: {e}"
        ti.xcom_push(key="extracted_reddit", value={"error": error_msg})
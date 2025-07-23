import os
from langchain_google_genai import ChatGoogleGenerativeAI as CGgenai
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import logging

def gemini_analysis_pipeline(ti):
    news_data = ti.xcom_pull(task_ids='transform_task', key='transformed_news')
    reddit_data = ti.xcom_pull(task_ids='transform_task', key='transformed_reddit')

    # Carga las variables de entorno desde el archivo .env
    load_dotenv()
    try:
        model = init_chat_model('gemini-2.5-flash', model_provider='google_genai')
    except Exception as e:
        ti.xcom_push(key="reddit_response",value={"gemini_response": str(e)})
        ti.xcom_push(key="news_response", value={"gemini_response": str(e)})
        logging.error(f"Error: There is not conection with gemini -> {e}")
        return

    if reddit_data['status'] == 'ok':
        reddit_posts = reddit_data['posts']

        prepared_reddit_posts = ""
        for i, post in enumerate(reddit_posts):
            prepared_reddit_posts = prepared_reddit_posts + f"Post {i+1}: {post.get('selftext', '')} \n"

        reddit_prompt= [HumanMessage(content=f"""As a model, give me a general overview of public opinion on Tesla
    in investment-related Reddit posts. Keep it brief, like a skimming. Respond directly and speak only in the third person.\n
    {prepared_reddit_posts}""")]
        
        try:
            reddit_response = model.invoke(reddit_prompt)
            reddit_response = reddit_response.content
        except Exception as e:
            reddit_response = f"Error while invoking Gemini for Reddit data: {str(e)}"

    else:
        reddit_response = "There was not reddit posts online in this week"

    ti.xcom_push(key="reddit_response",value={"gemini_response": reddit_response})

    ##########################################################################################################################
    articles = news_data['first_20_articles']

    prepared_news_descriptions = ""
    for i, article in enumerate(articles):
        prepared_news_descriptions = prepared_news_descriptions + f"Description {i+1} {article.get('description', '')} \n"

    news_prompt = [
        HumanMessage(content=f"""As a model, give me an investor-oriented overview of the general public opinion on Tesla based on news article descriptions. 
    Keep it brief, like a skimming. Respond directly and speak only in the third person.\n
    {prepared_news_descriptions}""")]

    try:
        news_response = model.invoke(news_prompt)
        news_response = news_response.content
    except Exception as e:
        news_response = f"Error while invoking Gemini for News data: {str(e)}"

    ti.xcom_push(key="news_response", value={"gemini_response": news_response})



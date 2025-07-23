import os
from langchain_google_genai import ChatGoogleGenerativeAI as CGgenai
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import logging
from pydantic import BaseModel, Field
from typing import Literal
import time


def gemini_labeling(ti):
    news_data = ti.xcom_pull(key="transformed_news", task_ids="transform_task")
    total_articles = news_data['first_20_articles']
    descriptions = [article ['description'] for article in total_articles]


    load_dotenv()

    # Carga las variables de entorno desde el archivo .env

    try:
        model = init_chat_model('gemini-2.5-flash', model_provider='google_genai')
    except Exception as e:
        ti.xcom_push(key="reddit_response",value={"gemini_response": str(e)})
        ti.xcom_push(key="news_response", value={"gemini_response": str(e)})
        logging.error(f"Error: There is not conection with gemini -> {e}")
        return
    
    class Clasificacion(BaseModel):
        feeling: Literal['Negative', 'Neutral', 'Positive', 'Other'] = Field(description='Investor-oriented sentiment classification based on the content’s tone and implications for Tesla.')

    structured_model = model.with_structured_output(Clasificacion)

    try:
        responses = []
        for description in descriptions:
            response = structured_model.invoke([
                {
                    'role':'user',
                    'content': f'''
                        Te voy a dar descripciones de noticias y necesito informacion, que salida sea en JSON formato:
            {description}
                    '''
                }
            ])
            responses.append(dict(response.model_dump()))
            time.sleep(3)
    except Exception as e:
        responses = f"Error -> {e}"

    ti.xcom_push(key="labeled_news", value=responses)

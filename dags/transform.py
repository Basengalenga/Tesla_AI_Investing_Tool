import logging
def transform(ti):
    try:
        tesla_data_with_meta_data = ti.xcom_pull(key="extracted_tesla", task_ids="extract_tesla_task")
        news_data = ti.xcom_pull(key="extracted_news", task_ids="extract_news_task")
        reddit_data = ti.xcom_pull(key="extracted_reddit", task_ids="extract_reddit_task")
    except Exception as e:
        logging.error(f"Couldn't pull the data from xcom --> {e}")
        return

    # Transform tesla
    try:
        tesla_data = tesla_data_with_meta_data['Time Series (Daily)']

        # Extraer los primeros 7 días como lista de tuplas (fecha, datos)
        first_7_days = list(tesla_data.items())[:7]

        # Extraer precios de cierre
        close_value_list = [float(values['4. close']) for _, values in first_7_days]

        clean_tesla_data = {
            'status': 'ok',
            'values': {
                date: {
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume']),
                } for date, values in first_7_days
            },
            'average_close': sum(close_value_list) / len(close_value_list),
            'volatility': max(close_value_list) - min(close_value_list)
        }

        ti.xcom_push(key='transformed_tesla', value=clean_tesla_data)
        logging.info("Tesla data successfully transformed")
    except Exception as e:
        ti.xcom_push(key='transformed_tesla', value={'status':'transforming_error'})
        logging.error(f"Couldn't transform tesla data --> {e}")

    # Transform news
    try:
        total_articles = news_data['totalResults']
        articles = [
            {
                'description': article['description'],
                'author': article['author'],
                'source': article['source']['name'],
            }
            for article in news_data['articles']
        ]

        first_20_articles = []
        for article in articles:
            if article['description']:
                first_20_articles.append(article)
            
            if len(first_20_articles) == 20:
                break

        clean_news_data = {
            'totalResults': total_articles,
            'first_20_articles': first_20_articles
        } 
        
        ti.xcom_push(key='transformed_news', value=clean_news_data)
        logging.info("News successfully transformed")
    except Exception as e:
        logging.error(f"Couldn't transform News data --> {e}")

    # Transform reddit data
    try:
        if reddit_data['status'] == 'ok':
            posts = reddit_data['posts']
            scores = [post['score']for post in posts]
            transformed_data ={
                'status': 'ok',
                'posts': [{
                    'selftext': post['selftext'],
                    'score': post['score']} for post in posts],
                'score_average': sum(scores) / len(scores)
            }
        elif reddit_data['status'] == "empty":
            transformed_data = reddit_data
            logging.info("No posts to transform — Reddit data is empty.")

        ti.xcom_push(key='transformed_reddit', value=transformed_data)
        logging.info("Reddit data successfully transformed")
    except Exception as e:
        logging.error(f"Couldn't transform reddit data --> {e}")
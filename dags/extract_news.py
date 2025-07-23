import requests 
from datetime import datetime, timedelta


def extraction_news(ti):
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    # URL con rango de fechas de 7 días
    URL = (
        'https://newsapi.org/v2/everything?'
        'q=Tesla&'
        f'from={from_date}&'
        f'to={to_date}&'
        'sortBy=popularity&'
        'pageSize=50&'  # Asegura que obtienes hasta 50 artículos (máximo por página)
        'apiKey=8cf7cf2ff5d94f66a26a673da77b9bb1'
    )

    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            ti.xcom_push(key="extracted_news", value=data)
        else:
            data = {"error": "Failed to fetch data, status code: " + str(response.status_code)}
            ti.xcom_push(key="extracted_news", value=data)
    except Exception as e:
        print(e)




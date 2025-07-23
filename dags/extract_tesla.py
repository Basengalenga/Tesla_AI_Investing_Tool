import requests
def extraction_tesla(ti):

    API_KEY = '9Y89VNCKF483V3TV'
    SYMBOL = 'TSLA'

    # URL para obtener los datos diarios de Tesla
    URL = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&outputsize=compact&apikey={API_KEY}'

    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        ti.xcom_push(key="extracted_tesla", value=data)
    else:
        data = {"error": "Failed to fetch data, status code: " + str(response.status_code)}
        ti.xcom_push(key="extracted_tesla", value=data)
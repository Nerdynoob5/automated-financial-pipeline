from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

from airflow.utils.log.logging_mixin import LoggingMixin

logger = LoggingMixin().log

def fetch_stock_data(api_key, symbol):
    base_url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if 'Time Series (Daily)' in data:
        df = pd.DataFrame(data['Time Series (Daily)']).transpose()
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)
        
        # Ensure 'data' directory exists
        os.makedirs('../data', exist_ok=True)
        
        df.to_excel(f'../data/{symbol}_stock_data.xlsx', index=False)
        logger.info(f"Stock data for {symbol} saved successfully.")
    else:
        logger.error("Error fetching data. Please check the API response.")

def scrape_yahoo_finance_news():
    url = 'https://finance.yahoo.com/topic/stock-market-news/'
    response = requests.get(url)
    
    if not response.ok:
        logger.error(f"Error fetching the URL: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract news data
    news_data = []
    articles = soup.find_all('li', class_='js-stream-content')

    if not articles:
        logger.warning("No articles found.")
    
    for article in articles:
        title_tag = article.find('h3')
        link_tag = article.find('a')
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = 'https://finance.yahoo.com' + link_tag['href']
            news_data.append({'Title': title, 'Link': link})
    
    if not news_data:
        logger.warning("No news data found.")
        return
    
    # Convert to DataFrame
    news_df = pd.DataFrame(news_data)
    logger.info(f"DataFrame preview:\n{news_df.head()}")
    
    # Ensure 'data' directory exists in the project root
    data_dir = os.path.join('C:', 'Users', 'Sudha Shukla', 'Desktop', 'automate', 'data')

    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, 'news_data.xlsx')
    logger.info(f"Saving file to: {file_path}")  # Debug print statement
    news_df.to_excel(file_path, index=False)
    logger.info(f"Data saved to {file_path}")

def etl_process():
    # File paths
    stock_data_path = '../data/AAPL_stock_data.xlsx'
    news_data_path = '../data/news_data.xlsx'
    transformed_stock_data_path = '../data/transformed_stock_data.xlsx'
    transformed_news_data_path = '../data/transformed_news_data.xlsx'

    # Load stock data
    try:
        stock_data = pd.read_excel(stock_data_path)
        logger.info(f"Stock Data Columns: {stock_data.columns}")
    except FileNotFoundError:
        logger.error(f"File not found: {stock_data_path}")
        return

    # Load news data
    try:
        news_data = pd.read_excel(news_data_path)
        logger.info(f"News Data Columns: {news_data.columns}")
    except FileNotFoundError:
        logger.error(f"File not found: {news_data_path}")
        return

    # Transform stock data
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    stock_data.set_index('Date', inplace=True)
    stock_data['Daily Change'] = stock_data['4. close'] - stock_data['1. open']

    # Perform basic analysis on stock data
    stock_summary = stock_data.resample('W').agg({
        '1. open': 'first',
        '4. close': 'last',
        'Daily Change': 'sum'
    })
    stock_summary.to_excel(transformed_stock_data_path)
    logger.info(f"Stock data transformed and saved to {transformed_stock_data_path}")

    # Transform news data
    news_data['Date'] = datetime.now().strftime('%Y-%m-%d')  # Adding a dummy date column for analysis
    news_summary = news_data.groupby('Date').size().reset_index(name='Count')
    news_summary.to_excel(transformed_news_data_path)
    logger.info(f"News data transformed and saved to {transformed_news_data_path}")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 9, 1),
}

# Define the DAG
dag = DAG(
    'financial_data_pipeline',
    default_args=default_args,
    description='A DAG for fetching, scraping, and processing financial data',
    schedule_interval=timedelta(days=1),  # Adjust the schedule as needed
)

# Define the tasks
start = DummyOperator(
    task_id='start',
    dag=dag,
)

fetch_stock_data_task = PythonOperator(
    task_id='fetch_stock_data',
    python_callable=fetch_stock_data,
    op_args=['70V21OEGRW3SHWFP', 'AAPL'],
    dag=dag,
)

scrape_news_data_task = PythonOperator(
    task_id='scrape_news',
    python_callable=scrape_yahoo_finance_news,
    dag=dag,
)

etl_process_task = PythonOperator(
    task_id='etl_process',
    python_callable=etl_process,
    dag=dag,
)


end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Define the task sequence
start >> [fetch_stock_data_task, scrape_news_data_task] >> etl_process_task >> end

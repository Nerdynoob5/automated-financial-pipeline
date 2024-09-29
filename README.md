# automated-financial-pipeline

# Financial Data Pipeline with Apache Airflow

This project is an automated financial data pipeline that uses Apache Airflow to scrape financial news from Yahoo Finance and fetch stock market data using the Alpha Vantage API. The results are stored in Excel files and can be visualized on a web dashboard.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Docker Setup](#docker-setup)
- [How to Run the Project](#how-to-run-the-project)


## Features
- Automated web scraping of financial news
- Integration with the Alpha Vantage API for stock data
- Data storage in Excel format
- Web dashboard for data visualization
- Dockerized environment for easy setup and deployment

## Technologies Used
- Apache Airflow
- Python
- BeautifulSoup (for web scraping)
- Pandas (for data manipulation)
- Alpha Vantage API
- Docker
- Excel (for data storage)

## Getting Started
### Prerequisites
- Docker and Docker Compose installed on your machine.
- A valid Alpha Vantage API key (you can obtain one [here](https://www.alphavantage.co/support/#api-key)).

# Docker Setup
This project uses Docker Compose to simplify the setup. The `docker-compose.yml` file defines the services required for the project.

## Building and Starting Services
To build and start the services, run:

```bash
docker-compose up --build

## How to Run the Project
After starting the Docker containers, access the Airflow web interface at `http://localhost:8080`.  
Log in with the default credentials (username: `airflow`, password: `airflow`).  
Trigger the DAG to start the data pipeline.



import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import lxml
from datetime import datetime
import sqlite3

url = 'https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
db_name = 'Banks.db'
csv_path = './Largest_banks_data.csv'
exchange_csv_path = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv'
table_name = 'Largest_banks'
log_file = 'code_log.txt'


def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(log_file, "a" ) as f:
        f.write(timestamp + ' : ' + message + '\n')


def extract(url, table_attribs):
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
            if col[1].find('a') is not None:
                data_dict = {"Name": col[1].find_all('a')[1].contents[0],
                             "MC_USD_Billion": float(col[2].contents[0])}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df, df1], ignore_index=True)
    return df


def transform(df, exchange_csv_path):
    money = pd.read_csv(exchange_csv_path)
    exchange_rate = money.set_index('Currency').to_dict()['Rate']
    gbp_rate = float(exchange_rate['GBP'])
    df['MC_GBP_Billion'] = [np.round(x * gbp_rate, 2) for x in df['MC_USD_Billion']]
    eur_rate = float(exchange_rate['EUR'])
    df['MC_EUR_Billion'] = [np.round(x * eur_rate, 2) for x in df['MC_USD_Billion']]
    inr_rate = float(exchange_rate['INR'])
    df['MC_INR_Billion'] = [np.round(x * inr_rate, 2) for x in df['MC_USD_Billion']]
    return df


def load_to_csv(df, csv_path):
    df.to_csv(csv_path)


def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists= 'replace', index = False)


def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

log_progress("Preliminaries complete. Initiating ETL process")

df = extract(url, table_attribs)
print(df)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df, exchange_csv_path)
#print (df['MC_EUR_Billion'][4])

log_progress('Data transformation complete. Initiating Loading process')

load_to_csv(df, csv_path)

log_progress("Data saved to CSV file")

sql_connection = sqlite3.connect(db_name)

log_progress("SQL Connection initiated")

load_to_db(df, sql_connection, table_name)

log_progress("Data loaded to Database as a table, Executing queries")

query_statement_1 = "SELECT * FROM Largest_banks"
run_query(query_statement_1, sql_connection)

query_statement_2 = "SELECT AVG(MC_GBP_Billion) FROM Largest_banks"
run_query(query_statement_2, sql_connection)

query_statement_3 = "SELECT Name FROM Largest_banks LIMIT 5"
run_query(query_statement_3, sql_connection)

log_progress("Process Complete")

sql_connection.close()

log_progress("Server Connection closed")

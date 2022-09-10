import requests
import json
from datetime import datetime
import os

from dateutil import parser

import pandas as pd


def get_data():
    '''Get the data from the API'''
    r = requests.post('http://ukwalls.epizy.com/?json')
    data = r.text.split('done a bad')[1]
    return json.loads(data)


def data_to_table(data, date=datetime.now()):
    '''Convert the data from the API into a list of lists'''
    data = list(data.items())
    scrape_date = date.date()
    scrape_time = date.time().strftime('%H:%M:%S')

    table = []
    for name, info in data:
        row = [scrape_date, scrape_time, name, info['capacity'],
               info['count'], info['lastUpdated']]
        table.append(row)

    return table


def update_df(df, table):
    '''Update the dataframe with the new data'''
    new_df = pd.DataFrame(data=table, columns=[
                          'scrape_date', 'scrape_time', 'name', 'capacity', 'count', 'time'])

    new_df = pd.concat([df, new_df], ignore_index=True)
    new_df.drop_duplicates(
        subset=['name', 'scrape_date', 'scrape_time'], keep='last')
    return new_df


def main():
    data = get_data()
    table = data_to_table(data)

    if not os.path.isfile('data/walls.csv'):
        df = pd.DataFrame(data=table, columns=[
                          'scrape_date', 'scrape_time', 'name', 'capacity', 'count', 'time'])
        df.to_csv('data/walls.csv', index=False)
        print('Saved collected data')
    else:
        df = pd.read_csv('data/walls.csv', skipinitialspace=True)
        print(df)
        df = update_df(df, table)
        print(df)
        df.to_csv('data/walls.csv', index=False)
        print('Saved updated data')


if __name__ == '__main__':
    main()

# %%
import json
import os
import re
import datetime
import time

import requests
import pandas as pd
import numpy as np

# Pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

url = "https://data.texas.gov/resource/naix-2893.json?"


# %%
def df_cities():
    query = f"""
        $select=distinct location_city&$limit=10000
    """

    query = re.sub(r'\n\s*', '', query).replace(' ', '%20')

    url_query = url + query

    return pd.read_json(url_query).rename(columns={'location_city':'City'})

df_cities = df_cities()
df_cities.head()


# %%
query = f"""
    $select=
        location_name,
        tabc_permit_number,
        location_number,
        location_address,
        location_city,
        min(obligation_end_date_yyyymmdd),
        max(obligation_end_date_yyyymmdd),
        sum(total_receipts),
        avg(total_receipts),
        sum(beer_receipts),
        avg(beer_receipts),
        sum(wine_receipts),
        avg(wine_receipts),
        sum(liquor_receipts),
        avg(liquor_receipts)
    &$group=
        location_name,
        tabc_permit_number,
        location_number,
        location_address,
        location_city
    &$where=
        obligation_end_date_yyyymmdd between '2020-02-01' and '2020-04-30'
        &location_city='{'DALLAS'.upper()}'
    &$order=sum_liquor_receipts DESC
    &$limit=100
"""

query = re.sub(r'\n\s*', '', query).replace(' ', '%20')

url_query = url + query

df = (
    pd.read_json(
        url_query, 
        convert_dates=['min_obligation_end_date_yyyymmdd', 'max_obligation_end_date_yyyymmdd']
    ).assign(
        min_obligation_beg_date_yyyymmdd = lambda x: x['min_obligation_end_date_yyyymmdd'] - pd.offsets.MonthBegin()
    )
)

df.head()


# %%
cols = ({
'location_name': {'rename': 'LocName', 'dtype': 'object'},
'tabc_permit_number': {'rename': 'LicNbr', 'dtype': 'object'},
'location_number': {'rename': 'LocNbr', 'dtype': 'object'},
'location_address': {'rename': 'Address', 'dtype': 'object'},
'location_city': {'rename': 'City', 'dtype': 'object'},
'min_obligation_beg_date_yyyymmdd': {'rename': 'BegDateMin','dtype': 'datetime64'},
'min_obligation_end_date_yyyymmdd': {'rename': 'EndDateMin','dtype': 'datetime64'},
'max_obligation_end_date_yyyymmdd': {'rename': 'EndDateMax','dtype': 'datetime64'},
'sum_total_receipts': {'rename': 'TotalSum', 'dtype': 'float64'},
'avg_total_receipts': {'rename': 'TotalAvg', 'dtype': 'float64'},
'sum_beer_receipts': {'rename': 'BeerSum', 'dtype': 'float64'},
'avg_beer_receipts': {'rename': 'BeerAvg', 'dtype': 'float64'},
'sum_wine_receipts': {'rename': 'WineSum', 'dtype': 'float64'},
'avg_wine_receipts': {'rename': 'WineAvg', 'dtype': 'float64'},
'sum_liquor_receipts': {'rename': 'LiqSum', 'dtype': 'float64'},
'avg_liquor_receipts': {'rename': 'LiqAvg', 'dtype': 'float64'}
})

for col in df.columns:
    
    try:
        temp_dict = cols[col]

        df[col] = df[col].astype(temp_dict['dtype'])
        
    except:
        pass

df = df.rename(columns={col:cols[col]['rename'] for col in cols})


df.head()


# %%
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)



# %%

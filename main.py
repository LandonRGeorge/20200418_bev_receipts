# %%
import json
import os
import re
import datetime
import time

import requests
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

# Pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

url_base = "https://data.texas.gov/resource/naix-2893.json?"


# %%
def df_cities():
    url_args = f"""
        $select=distinct location_city&$limit=10000
    """

    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    return pd.read_json(url_full).rename(columns={'location_city':'City'})

df_cities = df_cities()
df_cities.head()




# %%

def func_df_data(cities):
    """Grab data from TX Comptroller API"""


    text_cities = ''
    for i, city in enumerate(cities):
        text_temp = f"'{city}'"
        if i != len(cities) - 1:
            text_temp+=','
        text_cities+=text_temp

    url_args = f"""
        $select=
            location_name,
            tabc_permit_number,
            location_number,
            location_address,
            location_city,
            min(obligation_end_date_yyyymmdd),
            max(obligation_end_date_yyyymmdd),
            sum(total_receipts),
            sum(beer_receipts),
            sum(wine_receipts),
            sum(liquor_receipts)
        &$group=
            location_name,
            tabc_permit_number,
            location_number,
            location_address,
            location_city
        &$where=
            obligation_end_date_yyyymmdd between '2020-02-01' and '2020-04-30'
            and location_city in({text_cities})
        &$order=sum_liquor_receipts DESC
        &$limit=100
    """


    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    df = (
        pd.read_json(
            url_full, 
            convert_dates=['min_obligation_end_date_yyyymmdd', 'max_obligation_end_date_yyyymmdd']
        ).assign(
            min_obligation_beg_date_yyyymmdd = lambda x: x['min_obligation_end_date_yyyymmdd'] - pd.offsets.MonthBegin()
        )
    )

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
    'sum_beer_receipts': {'rename': 'BeerSum', 'dtype': 'float64'},
    'sum_wine_receipts': {'rename': 'WineSum', 'dtype': 'float64'},
    'sum_liquor_receipts': {'rename': 'LiqSum', 'dtype': 'float64'},
    })

    for col in df.columns:
        
        try:
            temp_dict = cols[col]

            df[col] = df[col].astype(temp_dict['dtype'])
            
        except:
            pass

    df = df.rename(columns={col:cols[col]['rename'] for col in cols})

    print(df.head(1))

    return df

df_data = func_df_data(cities=['WEATHERFORD','FRISCO'])
df_data.head()


# %%


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label':city, 'value':city} for city in df_cities['City'].unique()],
        value=['DALLAS'],
        multi=True
    ),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df_data.columns]
)
])

@app.callback(
    Output('table', 'data'),
    [Input('dropdown', 'value')])
def update_table(value):

    print(value)
    
    return func_df_data(value).to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)


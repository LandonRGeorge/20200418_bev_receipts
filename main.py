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

def df_cities():
    url_args = f"""
        $select=distinct location_city&$limit=10000
    """

    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    return pd.read_json(url_full).rename(columns={'location_city':'City'})

df_cities = df_cities()

def func_df_data(cities, segment):
    """Grab data from TX Comptroller API"""

    segment_dict = ({
        'TOTAL':'sum_total_receipts',
        'BEER':'sum_beer_receipts',
        'WINE':'sum_wine_receipts',
        'LIQUOR':'sum_liquor_receipts'
    })


    text_cities = ''
    for i, city in enumerate(cities):
        text_temp = f"'{city}'"
        if i != len(cities) - 1:
            text_temp+=','
        text_cities+=text_temp

    if cities:

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
                obligation_end_date_yyyymmdd between '2020-02-01' and '2020-02-29'
                and location_city in({text_cities})
            &$order={segment_dict[segment]} DESC
            &$limit=100
        """

    else:
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
                obligation_end_date_yyyymmdd between '2020-02-01' and '2020-02-29'
            &$order={segment_dict[segment]} DESC
            &$limit=100
        """


    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    df = (
        pd.read_json(
            url_full, 
            convert_dates=['min_obligation_end_date_yyyymmdd', 'max_obligation_end_date_yyyymmdd']
        ).assign(
            min_obligation_end_date_yyyymmdd = lambda x: x['min_obligation_end_date_yyyymmdd'] - pd.offsets.MonthBegin()
        ).rename(columns={'min_obligation_end_date_yyyymmdd':'min_obligation_beg_date_yyyymmdd'})
    )

    cols = ({
    'location_name': {'rename': 'LocName', 'dtype': 'object'},
    'tabc_permit_number': {'rename': 'LicNbr', 'dtype': 'object'},
    'location_number': {'rename': 'LocNbr', 'dtype': 'object'},
    'location_address': {'rename': 'Address', 'dtype': 'object'},
    'location_city': {'rename': 'City', 'dtype': 'object'},
    'min_obligation_beg_date_yyyymmdd': {'rename': 'BegDate','dtype': 'datetime64'},
    'max_obligation_end_date_yyyymmdd': {'rename': 'EndDate','dtype': 'datetime64'},
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

    return df

df_data = func_df_data(cities=[], segment='TOTAL')


app = dash.Dash(__name__)
server = app.server # the Flask app

app.layout = html.Div([
    html.H1('Mixed Beverage Gross Receipts'),
    html.P('Dataset API can be found at data.texas.gov'),
    html.Label('City Selection'),
    dcc.Dropdown(
        id='selection-cities',
        options=[{'label':city, 'value':city} for city in df_cities['City'].unique()],
        value=[],
        multi=True
    ),
    html.Label('Sort By Segment Selection'),
    dcc.RadioItems(
        id='selection-segment',
        options=[
            {'label':'TOTAL', 'value':'TOTAL'},
            {'label':'BEER', 'value':'BEER'},
            {'label':'WINE', 'value':'WINE'},
            {'label':'LIQUOR', 'value':'LIQUOR'}],
        value='TOTAL',
        labelStyle={'display': 'inline-block'}
    ),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df_data.columns]
)
])

@app.callback(
    Output('table', 'data'),
    [Input('selection-cities', 'value'),
     Input('selection-segment', 'value')])
def update_table(cities, segment):

    
    return func_df_data(cities, segment).to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)


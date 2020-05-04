
#%%import json
import os
import re
import datetime
import time

import requests
import pandas as pd
from pandas.tseries.offsets import DateOffset, MonthEnd, MonthBegin

import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from dash_table.Format import Format, Scheme, Sign, Symbol
import dash_table.FormatTemplate as FormatTemplate

# Pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

url_base = "https://data.texas.gov/resource/naix-2893.json?"

#%%
def get_date_range():
    """Get date range to feed into API query"""

    today = pd.Timestamp.today()
    
    # default end date to last day of previous month (from today)
    end_date = today - DateOffset(months=1) + MonthEnd()

    # default start date to first day of month 12 months ago
    start_date = end_date - DateOffset(months=11) - MonthBegin()

    def format_date(date):
        """Return date in `YYYY-mm-dd` format."""

        return date.to_pydatetime().strftime('%Y-%m-%d')

    return format_date(start_date), format_date(end_date)


start_date, end_date = get_date_range()

#%%

def df_cities():
    """Grab distinct listing of cities"""

    url_args = f"""
        $select=distinct location_city&$limit=10000
    """

    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    return pd.read_json(url_full).rename(columns={'location_city':'City'})

df_cities = df_cities()

#%%
def func_df_data(cities, segment, retailer, start_date, end_date):
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

    url_args_select_group_where = f"""
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
        &$where=obligation_end_date_yyyymmdd between '{start_date}' and '{end_date}'
    """

    if cities and retailer:

        url_args_where_opt = f"""
            and location_city in({text_cities})
            and location_name like '%25{retailer.upper()}%25'
        """

    elif cities:

        url_args_where_opt = f"and location_city in({text_cities})"


    elif retailer:

        url_args_where_opt = f"and location_name like '%25{retailer.upper()}%25'"


    else:

        url_args_where_opt = ""

    url_args = url_args_select_group_where + url_args_where_opt + f'&$order={segment_dict[segment]} DESC' + '&$limit=100'
    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    print(url_full)

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
    'location_address': {'rename': 'Address', 'dtype': 'object'},
    'location_city': {'rename': 'City', 'dtype': 'object'},
    'tabc_permit_number': {'rename': 'LicNbr', 'dtype': 'object'},
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

    cols_keep = [cols[col]['rename'] for col in cols]
    df = df.rename(columns={col:cols[col]['rename'] for col in cols}).loc[:,cols_keep]
    
    # doing this to get rid of timezone formatting in dash datatable
    # df = df.assign(
    #     BegDate = pd.DatetimeIndex(df['BegDate']).strftime("%Y-%m-%d"),
    #     EndDate = pd.DatetimeIndex(df['EndDate']).strftime("%Y-%m-%d")
    # )

    return df

df_data = func_df_data(cities=[], segment='TOTAL', retailer=None, start_date=start_date, end_date=end_date)

# #%%

# import plotly.offline as pyo
# import plotly.graph_objs as go
# import plotly as py

# fig = go.Figure()


# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["BeerSum"],
#         name="BeerSum",
#         text=df_data['LocName']
#         )
# )


# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["LiqSum"],
#         name="LiqSum",
#         text=df_data['LocName']
#         )
# )

# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["WineSum"],
#         name="WineSum",
#         text=df_data['LocName']
#         )
# )

# fig.update_layout(
#     go.Layout(
#         title=dict(
#             text='Total Receipts', y=0.9, x=0.5, xanchor="center", yanchor="top",
#         ),
#         barmode='stack',
#         hovermode="closest",
#         titlefont=dict(size=24, color="black"),
#         xaxis={'categoryorder':'category ascending'},
#         yaxis=dict(title="Total Receipts"),
#         yaxis_tickprefix="$",
#         yaxis_tickformat=",.",
#         template="plotly_white",  # can try plotly, plotly_white, ggplot, ggplot
#     )
# )

# fig.show()

#%%
app = dash.Dash(__name__)
server = app.server # the Flask app

app.layout = html.Div([
    html.H1('Mixed Beverage Gross Receipts'),
    html.P([
        "This dashboard uses the ",
        html.Em("Texas Comptroller of Public Accounts' "),
        html.A("Mixed Beverage Gross Receipts data", href = "https://data.texas.gov/Government-and-Taxes/Mixed-Beverage-Gross-Receipts/naix-2893", target="_blank"),
        ".",
    ]),
    html.P([
        "Make selections below to modify the results.",
    ]),
    html.P([
        "By default, the table shows the top 100 retailers, by total beverage gross receipts, for the state.",
    ]),
    html.Div([
        html.Label(html.Strong('Select one or more cities:')),
        dcc.Dropdown(
            id='selection-cities',
            options=[{'label':city, 'value':city} for city in df_cities['City'].unique()],
            value=[],
            multi=True,
            # style={'display': 'inline-block'}
        ),
        html.Br(),
        html.Label(html.Strong('Select a segment to sort gross receipts by:')),
        dcc.RadioItems(
            id='selection-segment',
            options=[
                {'label':'Total', 'value':'TOTAL'},
                {'label':'Beer', 'value':'BEER'},
                {'label':'Wine', 'value':'WINE'},
                {'label':'Liquor', 'value':'LIQUOR'}],
            value='TOTAL',
            # labelStyle={'display': 'inline-block'}
        ),
        html.Br(),
        html.Label(html.Strong('Search for a retailer by name (must hit `enter`):')),
        html.Br(),
        dcc.Input(id="selection-retailer", type="text", placeholder="", debounce=True),
        html.Br(),
        html.Br(),
        html.Label(html.Strong('Pick a date range:')),
        html.Br(),
        dcc.DatePickerRange(
            id='selection-date',
            start_date=start_date,
            end_date=end_date,
            start_date_placeholder_text="Start Period",
            end_date_placeholder_text="End Period",
            calendar_orientation='horizontal',
        )
    ]),
    html.Br(),
    dash_table.DataTable(
    id='table',
    columns=[
        {'id': 'LocName', 'name': 'Retailer Name', 'type': 'text'},
        {'id': 'Address', 'name': 'Address', 'type': 'text'},
        {'id': 'City', 'name': 'City', 'type': 'text'},
        {'id': 'LicNbr', 'name': 'License', 'type': 'text'},
        {'id': 'BegDate', 'name': 'Beg Date', 'type': 'datetime'},
        {'id': 'EndDate', 'name': 'End Date', 'type': 'datetime'},
        {'id': 'TotalSum', 'name': 'Total $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'BeerSum', 'name': 'Beer $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'WineSum', 'name': 'Wine $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'LiqSum', 'name': 'Liquor $', 'type': 'numeric', 'format': FormatTemplate.money(0)}
 ],
    fixed_rows={'headers': False},
    style_table={'height': 400},
    style_cell={'textAlign': 'left'},
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'right'
        } for c in ['TotalSum', 'BeerSum','WineSum','LiqSum']
    ],
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    # style_as_list_view=True, # removes vertical table dividers
)
])


@app.callback(
    Output('table', 'data'),
    [Input('selection-cities', 'value'),
     Input('selection-segment', 'value'),
     Input('selection-retailer', 'value'),
     Input('selection-date', 'start_date'),
     Input('selection-date', 'end_date')])
def update_table(cities, segment, retailer, start_date, end_date):

    print('inside update table', cities, segment, retailer, start_date, end_date)

    return func_df_data(cities, segment, retailer, start_date, end_date).to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=False)
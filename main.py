
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

from helper import dict_county_map

# Pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

#%%

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
def func_df_counties_cities():
    """Grab distinct listing of counties and cities"""

    url_args = f"""
        $select=distinct location_county, location_city&$limit=10000
    """

    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    df = (
        pd.read_json(url_full)
        .rename(columns={'location_county':'CountyNbr', 'location_city':'City'})
        .assign(CountyDesc = lambda x: x['CountyNbr'].map(dict_county_map))
        .sort_values(by=['CountyDesc','City'])
        )

    return df

df_counties_cities = func_df_counties_cities()
dict_counties_df = df_counties_cities[['CountyNbr','CountyDesc']].drop_duplicates().set_index('CountyNbr').iloc[:,0].to_dict()


#%%
def func_query_data(counties, cities, segment, retailer, start_date, end_date):
    """Grab data from TX Comptroller API"""

    url_args_select_group_where = f"""
        $select=
            location_name,
            tabc_permit_number,
            location_number,
            location_address,
            location_city,
            location_county,
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
            location_city,
            location_county
        &$where=obligation_end_date_yyyymmdd between '{start_date}' and '{end_date}'
    """


    def func_url_args_where():
        """Form a where clause for API query"""

        def comma_sep_str_from_list(list_input):
            """Return a comma and parantheses separated string from a list"""

            list_input_sep_paren = [f"'{elem}'" for elem in list_input]
            comma_sep_str =  ','.join(list_input_sep_paren)

            return comma_sep_str


        url_args_where_list = []
        
        if counties:

            url_args_where_list.append(f"location_county in({comma_sep_str_from_list(counties)})")
            
        if cities:

            url_args_where_list.append(f"location_city in({comma_sep_str_from_list(cities)})")
        
    
        if retailer:

            url_args_where_list.append(f"location_name like '%25{retailer.upper()}%25'")

        url_args_where_str = ' and '.join(url_args_where_list)

        if url_args_where_str:

            url_args_where_str = 'and ' + url_args_where_str

        return url_args_where_str


    url_args_where = func_url_args_where()

    url_args_order = f'&$order={segment} DESC'
    url_args_limit = '&$limit=1000'

    url_args = url_args_select_group_where + url_args_where + url_args_order + url_args_limit
    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    return url_full

query_data = func_query_data(counties=[], cities=[], segment='sum_total_receipts', retailer=None, start_date=start_date, end_date=end_date)


def func_df_data(query_data, segment):
    """Form dataframe from API query"""

    df = (
        pd.read_json(
            query_data, 
            convert_dates=['min_obligation_end_date_yyyymmdd', 'max_obligation_end_date_yyyymmdd']
        )
    )

    cols = ({
    'location_name': {'rename': 'LocName', 'dtype': 'object'},
    'location_address': {'rename': 'Address', 'dtype': 'object'},
    'location_city': {'rename': 'City', 'dtype': 'object'},
    'location_county': {'rename': 'CountyNbr', 'dtype': 'int64'},
    'tabc_permit_number': {'rename': 'LicNbr', 'dtype': 'object'},
    'min_obligation_end_date_yyyymmdd': {'rename': 'BegDate','dtype': 'datetime64'},
    'max_obligation_end_date_yyyymmdd': {'rename': 'EndDate','dtype': 'datetime64'},
    'sum_total_receipts': {'rename': 'sum_total_receipts', 'dtype': 'float64'},
    'sum_beer_receipts': {'rename': 'sum_beer_receipts', 'dtype': 'float64'},
    'sum_wine_receipts': {'rename': 'sum_wine_receipts', 'dtype': 'float64'},
    'sum_liquor_receipts': {'rename': 'sum_liquor_receipts', 'dtype': 'float64'},
    })

    for col in df.columns:
        
        try:
            temp_dict = cols[col]

            df[col] = df[col].astype(temp_dict['dtype'])
            
        except:
            pass
    

    cols_keep = [cols[col]['rename'] for col in cols]

    df = df.rename(columns={col:cols[col]['rename'] for col in cols}).loc[:,cols_keep]
    df = df.assign(
        CountyDesc = lambda x: x['CountyNbr'].map(dict_county_map),
        Rank = lambda x: x[segment].rank(method='dense', ascending=False),
        BegDateStr = lambda x: x['BegDate'].dt.strftime('%Y-%m'),
        EndDateStr = lambda x: x['EndDate'].dt.strftime('%Y-%m')
        )

    return df

df_data = func_df_data(query_data, segment='sum_total_receipts')



def data_bars(df, column, segment):
    """Add databars to Dash datatable, based on min and max values of column values."""

    # color selected segment a certain color; non-selected columns take a different color
    if column == segment:
        color = '#5CDB95'
        # color = '#0074D9' #blue
    else:
        color = '#cef4df'

    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    {color} 0%,
                    {color} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage, color=color)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles


#%%
app = dash.Dash(__name__)
server = app.server # the Flask app

app.layout = html.Div([
    html.H1('Mixed Beverage Gross Receipts'),
    html.P([
        "This dashboard uses the ",
        html.Em("Texas Comptroller of Public Accounts' "),
        html.A("Mixed Beverage Gross Receipts data", href = "https://data.texas.gov/Government-and-Taxes/Mixed-Beverage-Gross-Receipts/naix-2893", target="_blank"),
        ". By default, the table shows the top 100 retailers, by total beverage gross receipts, for the state.",
    ]),
    html.Div([

        html.Label(html.Strong('Select a segment to sort gross receipts by:')),
        dcc.RadioItems(
            id='selection-segment',
            options=[
                {'label':'Total $', 'value':'sum_total_receipts'},
                {'label':'Beer $', 'value':'sum_beer_receipts'},
                {'label':'Wine $', 'value':'sum_wine_receipts'},
                {'label':'Liquor $', 'value':'sum_liquor_receipts'}],
            value='sum_total_receipts',
            # labelStyle={'display': 'inline-block'}
        ),
        html.Br(),

        html.Label(html.Strong('Select one or more counties:')),
        dcc.Dropdown(
            id='selection-counties',
            options=[{'label':CountyDesc, 'value':CountyNbr} for CountyNbr,CountyDesc in dict_counties_df.items()],
            value=[],
            multi=True,
            # style={'display': 'inline-block'}
        ),
        html.Br(),

        html.Label(html.Strong('Select one or more cities:')),
        dcc.Dropdown(
            id='selection-cities',
            value=[],
            multi=True,
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
        {'id': 'Rank', 'name': '', 'type': 'text'},
        {'id': 'LocName', 'name': 'Retailer Name', 'type': 'text'},
        {'id': 'Address', 'name': 'Address', 'type': 'text'},
        {'id': 'CountyDesc', 'name': 'County', 'type': 'text'},
        {'id': 'City', 'name': 'City', 'type': 'text'},
        {'id': 'LicNbr', 'name': 'License', 'type': 'text'},
        {'id': 'BegDateStr', 'name': 'Beg Date', 'type': 'datetime'},
        {'id': 'EndDateStr', 'name': 'End Date', 'type': 'datetime'},
        {'id': 'sum_total_receipts', 'name': 'Total $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'sum_beer_receipts', 'name': 'Beer $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'sum_wine_receipts', 'name': 'Wine $', 'type': 'numeric', 'format': FormatTemplate.money(0)},
        {'id': 'sum_liquor_receipts', 'name': 'Liquor $', 'type': 'numeric', 'format': FormatTemplate.money(0)}
        ],
    # page_size=20,
    fixed_rows={'headers': True},
    style_table={'height': 1000},
    style_cell={'textAlign': 'left'},
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'right'
        } for c in ['sum_total_receipts', 'sum_beer_receipts','sum_wine_receipts','sum_liquor_receipts']
    ],
    style_header={
        'backgroundColor': '#636363',
        'color': 'white',
        'fontWeight': 'bold'
    },
    style_as_list_view=True,
)
])

@app.callback(
    [Output('table', 'data'),
    Output('table', 'style_data_conditional')],
    [Input('selection-counties', 'value'),
     Input('selection-cities', 'value'),
     Input('selection-segment', 'value'),
     Input('selection-retailer', 'value'),
     Input('selection-date', 'start_date'),
     Input('selection-date', 'end_date')])
def update_table(counties, cities, segment, retailer, start_date, end_date):
    """Update datatable"""

    query_data = func_query_data(counties, cities, segment, retailer, start_date, end_date)
    df_data = func_df_data(query_data, segment)


    style_data_conditional = (
        data_bars(df_data, 'sum_total_receipts', segment) +
        data_bars(df_data, 'sum_beer_receipts', segment) +
        data_bars(df_data, 'sum_wine_receipts', segment) +
        data_bars(df_data, 'sum_liquor_receipts', segment)
    )


    return df_data.to_dict('records'), style_data_conditional


@app.callback(
    Output('selection-cities', 'options'),
    [Input('selection-counties', 'value')])
def set_display_cities(counties, df=df_counties_cities):
    """Return all possible cities that could be selected, based on what has been selected from counties"""    

    if counties:

        cities = df[df['CountyNbr'].isin(counties)].loc[:,'City'].unique().tolist()

    else:

        cities = df['City'].unique().tolist()

    return [{'label':city, 'value':city} for city in sorted(cities)]


if __name__ == '__main__':
    app.run_server(debug=True)
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
#%%

def func_df_retailer(tabc_permit_number):
    """Grab single-retailer data from TX Comptroller API"""

    url_args = f"""
        $select=
            location_name,
            tabc_permit_number,
            location_number,
            location_address,
            location_city,
            obligation_end_date_yyyymmdd,
            total_receipts,
            beer_receipts,
            wine_receipts,
            liquor_receipts
        &$where=
            tabc_permit_number = '{tabc_permit_number}'
            and total_receipts > 0
        &$order=tabc_permit_number, obligation_end_date_yyyymmdd ASC
    """

    url_args = re.sub(r'\n\s*', '', url_args).replace(' ', '%20')

    url_full = url_base + url_args

    df = (
        pd.read_json(
            url_full, 
            convert_dates=['obligation_end_date_yyyymmdd']
        ).assign(
            obligation_beg_date_yyyymmdd = lambda x: x['obligation_end_date_yyyymmdd'] - pd.offsets.MonthBegin()
        ).rename(columns={'min_obligation_end_date_yyyymmdd':'min_obligation_beg_date_yyyymmdd'})
    )

    cols = ({
    'location_name': {'rename': 'LocName', 'dtype': 'object'},
    'location_address': {'rename': 'Address', 'dtype': 'object'},
    'location_city': {'rename': 'City', 'dtype': 'object'},
    'tabc_permit_number': {'rename': 'LicNbr', 'dtype': 'object'},
    'obligation_beg_date_yyyymmdd': {'rename': 'BegDate','dtype': 'datetime64'},
    'obligation_end_date_yyyymmdd': {'rename': 'EndDate','dtype': 'datetime64'},
    'total_receipts': {'rename': 'TotalSum', 'dtype': 'float64'},
    'beer_receipts': {'rename': 'BeerSum', 'dtype': 'float64'},
    'wine_receipts': {'rename': 'WineSum', 'dtype': 'float64'},
    'liquor_receipts': {'rename': 'LiqSum', 'dtype': 'float64'},
    })

    for col in df.columns:
        
        try:
            temp_dict = cols[col]

            df[col] = df[col].astype(temp_dict['dtype'])
            
        except:
            pass

    cols_keep = [cols[col]['rename'] for col in cols]
    df = df.rename(columns={col:cols[col]['rename'] for col in cols}).loc[:,cols_keep]

    return df


# %%

df_retailer = func_df_retailer(tabc_permit_number='MB835465')

#%%
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly as py

fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["BeerSum"],
        mode="lines + markers",
        name="BeerSum"
        )
)

fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["WineSum"],
        mode="lines + markers",
        name="WineSum"
        )
)

fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["LiqSum"],
        mode="lines + markers",
        name="LiqSum"
        )
)

fig.update_layout(
    go.Layout(
        title=dict(
            text=df_retailer['LocName'].iloc[0], y=0.9, x=0.5, xanchor="center", yanchor="top",
        ),
        hovermode="closest",
        titlefont=dict(size=24, color="black"),
        # xaxis=dict(title="Month"),
        yaxis=dict(title="Total Receipts"),
        yaxis_tickprefix="$",
        yaxis_tickformat=",.",
        template="plotly_white",  # can try plotly, plotly_white, ggplot, ggplot
    )
)

fig.show()


# %%
fig = go.Figure()



fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["WineSum"],
        mode="lines",
        name="WineSum",
        stackgroup='one'
        )
)

fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["LiqSum"],
        mode="lines",
        name="LiqSum",
        stackgroup='one'
        )
)
fig.add_trace(
    go.Scatter(
        x=df_retailer["EndDate"],
        y=df_retailer["BeerSum"],
        mode="lines",
        name="BeerSum",
        stackgroup='one',
        groupnorm='percent' # sets the normalization for the sum of the stackgroup
        )
)

fig.update_layout(
    go.Layout(
        title=dict(
            text=df_retailer['LocName'].iloc[0], y=0.9, x=0.5, xanchor="center", yanchor="top",
        ),
        hovermode="closest",
        titlefont=dict(size=24, color="black"),
        # xaxis=dict(title="Month"),

        showlegend=True,
        yaxis=dict(
            title="Total Receipts Pct",
            type='linear',
            range=[1, 100],
            ticksuffix='%'),

        template="plotly_white",  # can try plotly, plotly_white, ggplot, ggplot
    )
)

fig.show()


# %%

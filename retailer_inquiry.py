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
    &$where=tabc_permit_number = 'MB522802'
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
    )
)

#%%
df.head()
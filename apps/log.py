import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import sqlalchemy as alch
from dash.dependencies import Input, Output, State

from app import app
from modules import navbar, styleTable, styleHeader, styleCell

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT *
FROM loghistory
ORDER BY log_date_cr
'''

AllColumns = {'log_id':'ID',
              'log_menu_name':'Menu',
              'log_activity':'Aktivitas',
              'log_date_cr':'Tanggal',
              'log_by_cr':'User'}


df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = AllColumns)

log_layout = html.Div([
    dcc.Location(id='log-url', pathname='/log'),
    dcc.Interval(
        id='interval-log',
        disabled=False,
        interval=5 * 1000,
        n_intervals=0,
        max_intervals= -1
    ),
    navbar(),

    html.Div(id='table-container-log',children=[
        html.H1('Log', id='log-header'),
        dt.DataTable(
            id='table-log',
            columns= [{'name':i,'id':i} for i in df_renamed.columns],
            filter_action='native',
            editable=False,
            row_deletable=False,
            sort_action='native',
            sort_mode='single',
            page_action="native",
            page_current=0,
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell(),
            style_header=styleHeader(),
            fixed_rows={'headers': True},
        )
    ])
])

@app.callback(
    Output('table-log','data'),
    [Input('interval-log','n_intervals')]
)
def viewLog(n):
    df = pd.read_sql(query,engine)
    df['log_date_cr'] = pd.to_datetime(df['log_date_cr']).dt.strftime('%d-%m-%Y %H:%M:%S')
    df_renamed = df.rename(columns = AllColumns)
    data = df_renamed.to_dict('records')
    return data
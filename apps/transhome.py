import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlalchemy as alch

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime

from app import app
from modules import navbar

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT trans_driver, trans_vehicle, trans_product_type, trans_sent_date, trans_received_date
FROM transactiondelivery;
'''
query2 = '''
SELECT trans_driver, trans_vehicle, trans_product_type, trans_sent_date, trans_received_date, trans_date_cr
FROM transactiondelivery;
'''


df = pd.read_sql(query,engine)
df['tgl_terima'] = df['trans_received_date']
df.set_index('tgl_terima',inplace=True)
df_renamed = df.rename(columns = {'trans_driver':'Nama Driver', 
                                  'trans_vehicle':'Jenis Pengiriman', 
                                  'trans_product_type':'Jenis Produk', 
                                  'trans_sent_date':'Tanggal Kirim', 
                                  'trans_received_date':'Tanggal Terima'})


df2 = pd.read_sql(query2, engine)
df2['tgl_dibuat'] = df2['trans_date_cr']
df2.set_index('tgl_dibuat', inplace=True)
df2_renamed = df2.rename(columns = {'trans_driver':'Nama Driver', 
                                  'trans_vehicle':'Jenis Pengiriman', 
                                  'trans_product_type':'Jenis Produk', 
                                  'trans_sent_date':'Tanggal Kirim', 
                                  'trans_received_date':'Tanggal Terima',
                                  'trans_date_cr':'Tanggal Transaksi'})

styleTable={
    'height':'380px', 
    'width':'100%',
    'overflowX':'auto'
}
styleHeader={
    'backgroundColor':'rgb(200,200,200)',
    'fontWeight':'bold',
    'width':'auto'
}
styleCell={
    'textAlign':'center',
    'backgroundColor':'rgb(240,240,240)',
    'width':'auto',
    'fontSize':'12pt',
    'height':'auto',
    'whiteSpace':'normal'
}

transhome_layout = html.Div([
    dcc.Location(id='transhome-url',pathname='/transhome'),
    dcc.Interval(
        id='interval-transhome',
        disabled=False,
        interval=3600*1000, #3.600.000 miliseconds
        n_intervals=0,
        max_intervals=-1 #unlimited, 0 stop
    ),
    navbar(),
    html.H1('Dashboard Transaksi', id='transhome-header'),
    html.Div(id='transhome-content',children=[

        html.Div(id='date-container-sent',children=[
            html.Div(id='top-sent', children=[
                html.Label('Tanggal terima', id='label-transhome'),
                dcc.DatePickerRange(
                    id='date-picker-sent',
                    display_format='DD-MM-YYYY',
                    min_date_allowed=datetime(2000, 1, 1),
                    max_date_allowed=datetime(2050, 12, 31),
                    initial_visible_month=datetime.today(),
                    with_portal=True,
                    stay_open_on_select=True,
                    clearable=True
                )
            ]),
            html.Div(id='table-container-received',children=[
                    dt.DataTable(id='data-table-received')
            ])
        ]),
        html.Div(id='date-container-trans', children=[
            html.Div(id='top-trans',children=[
                html.Label('Tanggal transaksi', id='label-transhome'),
                dcc.DatePickerRange(
                    id='date-picker-trans',
                    display_format='DD-MM-YYYY',
                    min_date_allowed=datetime(2000, 1, 1),
                    max_date_allowed=datetime(2050, 12, 31),
                    initial_visible_month=datetime.today(),
                    with_portal=True,
                    stay_open_on_select=True,
                    clearable=True
                )
            ]),
            html.Div(id='table-container-created',children=[
                dt.DataTable(id='data-table-created')
            ])

        ])
    ])
])

@app.callback(
    Output('table-container-received', 'children'),
    [Input('date-picker-sent', 'start_date'), Input('date-picker-sent', 'end_date')]
)
def getReceivedData(start_date, end_date):
    df_rec = df_renamed.loc[start_date: end_date]
    return dt.DataTable(
                id='data-table-received',
                columns=[{'name':i,'id':i} for i in df_renamed.columns],
                data = df_rec.to_dict('records'),
                style_table=styleTable,
                style_cell=styleCell,
                style_header=styleHeader, 
                sort_action='native',
                sort_mode='single',
                page_action='native',
                page_current=0,
                page_size=10
            )

@app.callback(
    Output('data-table-received','data'),
    [Input('interval-transhome','n_intervals')]
)
def refReceived(interval):
    if interval == 0:
        raise PreventUpdate
    else:
        df = pd.read_sql(query,engine)
        df['tgl_terima'] = df['trans_received_date']
        df.set_index('tgl_terima',inplace=True)
        df_renamed = df.rename(columns = {'trans_driver':'Nama Driver', 
                                        'trans_vehicle':'Jenis Pengiriman', 
                                        'trans_product_type':'Jenis Produk', 
                                        'trans_sent_date':'Tanggal Kirim', 
                                        'trans_received_date':'Tanggal Terima'})
        data = df_renamed.to_dict('records')
    return data


@app.callback(
    Output('table-container-created','children'),
    [Input('date-picker-trans','start_date'), Input('date-picker-trans','end_date')]
)
def getCreatedData(start_date, end_date):
    df_cr = df2_renamed.loc[start_date: end_date]
    return dt.DataTable(
                id='data-table-created',
                columns=[{'name':i,'id':i} for i in df2_renamed.columns],
                data=df_cr.to_dict('records'),
                style_table=styleTable,
                style_cell=styleCell,
                style_header=styleHeader,
                sort_action='native',
                sort_mode='single',
                page_action='native',
                page_current=0,
                page_size=10
            )

@app.callback(
    Output('data-table-created','data'),
    [Input('interval-transhome','n_intervals')]
)
def refCreated(interval):
    if interval == 0:
        raise PreventUpdate
    else:
        df2 = pd.read_sql(query2, engine)
        df2['tgl_dibuat'] = df2['trans_date_cr']
        df2.set_index('tgl_dibuat', inplace=True)
        df2_renamed = df2.rename(columns = {'trans_driver':'Nama Driver', 
                                            'trans_vehicle':'Jenis Pengiriman', 
                                            'trans_product_type':'Jenis Produk', 
                                            'trans_sent_date':'Tanggal Kirim', 
                                            'trans_received_date':'Tanggal Terima',
                                            'trans_date_cr':'Tanggal Transaksi'})
        data = df2_renamed.to_dict('records')
    return data
import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import sqlalchemy as alch
import time
from dash.dependencies import Input, Output, State

from app import app
from modules import navbarUser, styleTable, styleHeader
from apps import login

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT us.user_name, us.user_location, td.trans_product_type, td.trans_amount, td.trans_store, td.trans_city, td.trans_invoice, td.trans_status, td.trans_sent_date, td.trans_received_date
FROM transactiondelivery as td, mstrusers as us
WHERE td.trans_store = us.user_location
ORDER BY td.trans_sent_date
'''

AllColumns = {'user_name':'Nama', 
              'trans_city':'Kota Tujuan',
              'trans_product_type':'Tipe Produk',
              'trans_amount':'Harga',
              'trans_store':'Toko Tujuan',
              'trans_invoice':'No. Resi',
              'trans_status':'Status',
              'trans_sent_date':'Tanggal Kirim',
              'trans_received_date':'Tanggal Terima'}
                 
styleCell={
    'textAlign':'center',
    'backgroundColor':'rgb(240,240,240)',
    'width':'50px',
    'fontSize':'12pt',
    'height':'auto',
    'whiteSpace':'normal'
}

df = pd.read_sql(query, engine)
df_renamed = df.rename(columns = AllColumns)

options = [{'label': 'Harga', 'value': 'trans_amount'},
           {'label': 'Toko Tujuan', 'value': 'trans_store'},
           {'label': 'Status', 'value': 'trans_status'},
           {'label': 'Tanggal Kirim', 'value': 'trans_sent_date'}]

def filter_data():
    df = pd.read_sql(query, engine)
    df_renamed = df.rename(columns = AllColumns)
    name = login.logged_name
    location = login.logged_location
    df_renamed = df.loc[df['user_location'] == location]
    df_renamed2 = df_renamed.loc[df['user_name'] == name]
    df_renamed2['trans_sent_date'] = pd.to_datetime(df_renamed2['trans_sent_date']).dt.strftime('%d-%m-%Y %H:%M:%S')
    df_renamed2['trans_received_date'] = pd.to_datetime(df_renamed2['trans_received_date']).dt.strftime('%d-%m-%Y %H:%M:%S')

    df_renamed2['trans_amount'] = df_renamed2.apply(lambda x: "{:,}".format(x['trans_amount']), axis=1)

    df_filtered = df_renamed2.rename(columns = AllColumns)
    data = df_filtered.to_dict('records')
    return data

def filter_data_chart():
    df = pd.read_sql(query, engine)
    name = login.logged_name
    location = login.logged_location
    df = df.loc[df['user_location'] == location]
    df2 = df.loc[df['user_name'] == name]

    df2['trans_sent_date'] = pd.to_datetime(df2['trans_sent_date']).dt.strftime('%d-%m-%Y %H:%M:%S')
    return df2

user_view_layout = html.Div([
    dcc.Location(id='user-view-url', pathname='/user-view'),
    dcc.Interval(
        id='interval-user-view',
        disabled=False,
        interval=120 * 1000,
        n_intervals=0,
        max_intervals=-1
    ),
    dcc.Interval(
        id='interval-table-user-view',
        disabled=False,
        interval=15 * 1000,
        n_intervals=0,
        max_intervals=-1
    ),
    navbarUser(),
    html.H1('Daftar Transaksi', id='user-view-header'),
    html.Div(id='name-user-view'),
    html.Div(id='table-user-view',children=[
        dt.DataTable(
            id='data-table-user-view',
            columns=[
                {'name':'Nama', 'id':'Nama', 'editable': False},
                {'name':'Tipe Produk', 'id':'Tipe Produk', 'editable': False},
                {'name':'Harga', 'id':'Harga', 'editable': False},
                {'name':'Toko Tujuan', 'id':'Toko Tujuan', 'editable': False},
                {'name':'Kota Tujuan', 'id':'Kota Tujuan', 'editable': False},
                {'name':'No. Resi', 'id':'No. Resi', 'editable': False},
                {'name':'Status', 'id':'Status', 'editable': False},
                {'name':'Tanggal Kirim', 'id':'Tanggal Kirim', 'editable': False},
                {'name':'Tanggal Terima', 'id':'Tanggal Terima', 'editable': False},
            ],
            filter_action='native',
            editable=False,
            row_deletable=False,
            page_action="native",
            page_current=0,
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell,
            style_header=styleHeader(),
            fixed_rows={'headers': True},
        )
    ]),

    html.Div(id='user-view-content',children=[
        html.Div(id='pie-container-user', children=[
            html.Label('PILIHAN', className='pilihan-user'),
            dcc.Dropdown(id='dropdown-pie-user',
                 options=options,
                 optionHeight=25, #jarak antara pilihan
                 value='trans_store', #default value
                 disabled=False, #dropdownnya didisable
                 searchable=True,
                 multi=False,
                 placeholder='Select here',
                 clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='pie-chart-user')], size="lg", color="primary", type='border', fullscreen=False),
        ]),

        html.Div(id='line-container-user',children=[
            html.Label('PILIHAN 1', className='pilihan-user'),
            dcc.Dropdown(id='dropdown-line-1-user',
                    options=options,
                    optionHeight=25, 
                    value='trans_sent_date',
                    disabled=False,
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            html.Label('PILIHAN 2', className='pilihan-user'),
            dcc.Dropdown(id='dropdown-line-2-user',
                    options=options,
                    optionHeight=25, 
                    value='trans_status', 
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='line-chart-user')], size="lg", color="primary", type='border', fullscreen=False),
        ]),

        html.Div(id='bar-container-user',children=[
            html.Label('PILIHAN 1', className='pilihan-user'),
            dcc.Dropdown(id='dropdown-bar-1-user',
                    options=options,
                    optionHeight=25,
                    value='trans_sent_date', 
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            html.Label('PILIHAN 2', className='pilihan-user'),
            dcc.Dropdown(id='dropdown-bar-2-user',
                    options=options,
                    optionHeight=25, 
                    value='trans_status',
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='bar-chart-user')], size="lg", color="primary", type='border', fullscreen=False),
        ])
    ])
])


@app.callback(
    Output('name-user-view','children'),
    [Input('interval-user-view','n_intervals')]
)
def user_name(n):
    name = login.logged_name
    location = login.logged_location
    return 'Halo, ' + name

@app.callback(
    Output('data-table-user-view','data'),
    [Input('interval-table-user-view','n_intervals')]
)
def table_view(n):
    rows = filter_data()
    return rows

@app.callback(
    Output('pie-chart-user','figure'),
    [Input('dropdown-pie-user','value')]
)
def PieChart(chosen_column):
    df = pd.read_sql(query,engine)
    df = filter_data_chart()
    fig = px.pie(data_frame=df, names=chosen_column, labels={
                                                                'trans_store':'Toko Tujuan',
                                                                'trans_amount':'Harga',
                                                                'trans_status':'Status',
                                                                'trans_sent_date':'Tanggal Kirim'
                                                            })
    fig.update_traces(textinfo='percent', hovertemplate="<b>Label</b>:<br>%{label}<br><br><b>Value:</b>:<br>%{value}<br>")
    fig.update_layout(title = {'text':'Pie Chart'})
    return (fig)

@app.callback(
    Output('line-chart-user','figure'),
    [Input('dropdown-line-1-user','value'), Input('dropdown-line-2-user','value')]
)
def LineChart(chosen_column_1, chosen_column_2):
    df = pd.read_sql(query,engine)
    df = filter_data_chart()
    fig = px.line(df, x=chosen_column_1, y=chosen_column_2, labels={
                                                                    'trans_store':'Toko Tujuan',
                                                                    'trans_amount':'Harga',
                                                                    'trans_status':'Status',
                                                                    'trans_sent_date':'Tanggal Kirim'
    })

    fig.update_traces(mode='lines+markers')
    fig.update_layout(title = {'text':'Line Chart'})
    fig.update_layout(hoverlabel=dict(
                            bgcolor="white",
                            font_size=16,
                            font_family="sansserif"))
    return (fig)

@app.callback(
    Output('bar-chart-user','figure'),
    [Input('dropdown-bar-1-user','value'), Input('dropdown-bar-2-user','value')]
)
def BarChart(chosen_column_1, chosen_column_2):
    df = pd.read_sql(query,engine)
    df = filter_data_chart()
    fig = px.bar(df, x=chosen_column_1, y=chosen_column_2, labels={
                                                                    'trans_store':'Toko Tujuan',
                                                                    'trans_amount':'Harga',
                                                                    'trans_status':'Status',
                                                                    'trans_sent_date':'Tanggal Kirim'
    })
    fig.update_traces(marker_color='green')
    fig.update_layout(title = {'text':'Bar Chart'})
    fig.update_layout(hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                        font_family="sansserif"))
    return (fig)
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlalchemy as alch
from dash.dependencies import Input, Output
from dash import no_update
from flask import session, copy_current_request_context

from app import app
from apps import login
from modules import navbar

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')

query = '''
SELECT trans_driver, trans_product_type, trans_store, trans_city, trans_amount
FROM transactiondelivery;
'''
df = pd.read_sql(query,engine)

options = [{'label': 'Nama Driver', 'value': 'trans_driver'},
           {'label': 'Tipe Produk', 'value': 'trans_product_type'},
           {'label': 'Toko Tujuan', 'value': 'trans_store'},
           {'label': 'Kota Tujuan', 'value': 'trans_city'},
           {'label': 'Harga', 'value': 'trans_amount'}]

layout = html.Div([
    dcc.Location(id='home-url',pathname='/home'),
    navbar(),
    
    html.Div(id='home-content',children=[
        html.Div(id='pie-container', children=[
            html.Label('PILIHAN', className='pilihan'),
            dcc.Dropdown(id='dropdown-pie',
                 options=options,
                 optionHeight=25, #jarak antara pilihan
                 value='trans_city', #default value
                 disabled=False, #dropdownnya didisable
                 searchable=True,
                 multi=False,
                 placeholder='Select here',
                 clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='pie-chart-home')], size="lg", color="primary", type='border', fullscreen=True),
            
        ]),

        html.Div(id='line-container',children=[
            html.Label('PILIHAN 1', className='pilihan'),
            dcc.Dropdown(id='dropdown-line-1',
                    options=options,
                    optionHeight=25, 
                    value='trans_driver',
                    disabled=False,
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            html.Label('PILIHAN 2', className='pilihan'),
            dcc.Dropdown(id='dropdown-line-2',
                    options=options,
                    optionHeight=25, 
                    value='trans_city', 
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='line-chart-home')], size="lg", color="primary", type='border', fullscreen=True),
        ]),

        html.Div(id='bar-container',children=[
            html.Label('PILIHAN 1', className='pilihan'),
            dcc.Dropdown(id='dropdown-bar-1',
                    options=options,
                    optionHeight=25,
                    value='trans_driver', 
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            html.Label('PILIHAN 2', className='pilihan'),
            dcc.Dropdown(id='dropdown-bar-2',
                    options=options,
                    optionHeight=25, 
                    value='trans_city',
                    disabled=False, 
                    searchable=True,
                    multi=False,
                    placeholder='Select here',
                    clearable=True
            ),
            dbc.Spinner(children=[dcc.Graph(id='bar-chart-home')], size="lg", color="primary", type='border', fullscreen=True),
        ])
    ])
])



@app.callback(
    Output('pie-chart-home','figure'),
    [Input('dropdown-pie','value')]
)
def PieChart(chosen_column):
    df = pd.read_sql(query,engine)
    df_temp = df
    fig = px.pie(data_frame=df_temp, names=chosen_column, labels={
                                                                    'trans_driver':'Nama Driver',
                                                                    'trans_product_type':'Tipe Produk',
                                                                    'trans_store':'Toko Tujuan',
                                                                    'trans_city':'Kota Tujuan',
                                                                    'trans_amount':'Harga'
    })
    fig.update_traces(textinfo='percent', hovertemplate="<b>Label</b>:<br>%{label}<br><br><b>Value:</b>:<br>%{value}<br>")
    fig.update_layout(title = {'text':'Pie Chart'})
    return (fig)

@app.callback(
    Output('line-chart-home','figure'),
    [Input('dropdown-line-1','value'), Input('dropdown-line-2','value')]
)
def LineChart(chosen_column_1, chosen_column_2):
    df = pd.read_sql(query,engine)
    df_temp = df
    fig = px.line(df_temp, x=chosen_column_1, y=chosen_column_2, labels={
                                                                    'trans_driver':'Nama Driver',
                                                                    'trans_product_type':'Tipe Produk',
                                                                    'trans_store':'Toko Tujuan',
                                                                    'trans_city':'Kota Tujuan',
                                                                    'trans_amount':'Harga'
    })

    fig.update_traces(mode='lines+markers')
    fig.update_layout(title = {'text':'Line Chart'})
    fig.update_layout(hoverlabel=dict(
                            bgcolor="white",
                            font_size=16,
                            font_family="sansserif"))
    return (fig)

@app.callback(
    Output('bar-chart-home','figure'),
    [Input('dropdown-bar-1','value'), Input('dropdown-bar-2','value')]
)
def BarChart(chosen_column_1, chosen_column_2):
    df = pd.read_sql(query,engine)
    df_temp = df
    fig = px.bar(df_temp, x=chosen_column_1, y=chosen_column_2, labels={
                                                                    'trans_driver':'Nama Driver',
                                                                    'trans_product_type':'Tipe Produk',
                                                                    'trans_store':'Toko Tujuan',
                                                                    'trans_city':'Kota Tujuan',
                                                                    'trans_amount':'Harga'
    })
    fig.update_traces(marker_color='green')
    fig.update_layout(title = {'text':'Bar Chart'})
    fig.update_layout(hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                        font_family="sansserif"))
    return (fig)

@app.callback(
    Output('home-url','pathname'),
    [Input('logout-link', 'n_clicks')]
)
def logoutCLick(n):
    if n is None or n == 0:
        return no_update
    session['authed'] = False
    login.setUser('','','','','')
    a = login.logged_email
    print(a)
    return '/'
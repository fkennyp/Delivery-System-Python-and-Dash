import dash
import pyodbc 
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import sqlalchemy as alch
from dash.dependencies import Input, Output, State
from dash import no_update

from app import app
from modules import navbar, styleTable, styleHeader, styleCell

# cnxn = pyodbc.connect(
#                      "DRIVER={SQL Server};"
#                      "SERVER=101.255.140.117,1979;"
#                      "DATABASE=DATACOURIER;"
#                      "UID=admgab1;"
#                      "PWD=G4B@2020++;")

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query_tri = '''
SELECT tr.Airwaybill, tr.Redock, tr.Tanggal, tr.Customer, tr.Consignee, tr.Weight, tr.Meas, tr.Collie, tr.Moda, tr.Destination, tr.ReceiveBy, tr.ReceiveTgl, his.Keterangan
FROM _GAB_HISTORY as his, _GAB_TRANSAKSI as tr
WHERE his.Airwaybill = tr.Airwaybill 
'''
query_couriers = '''
SELECT courier_name
FROM mstrcouriers
'''

df_couriers = pd.read_sql(query_couriers, engine)
couriers = [{'label':x,'value':x} for x in df_couriers['courier_name']]

cekresi_layout = html.Div([
    dcc.Location(id='cekresi-url', pathname='/cekresi'),
    dcc.Interval(
        id='interval-options-cekresi',
        disabled=False,
        interval=15 * 1000,
        n_intervals=0,
        max_intervals= -1
    ),
    navbar(),
    
    html.H1('Cek Resi', id='cekresi-header'),
    dbc.Row(
        dbc.Col([
            dbc.FormGroup([
                html.Hr(),
                dbc.Label('Kurir :', className='label-cekresi'),
                dcc.Dropdown(id='dropdown-courier-cekresi',
                                options= couriers,
                                optionHeight=25, 
                                disabled=False, 
                                searchable=True,
                                multi=False,
                                placeholder='Pilih kurir...',
                                clearable=True
                        ),
                html.Br(),
                dbc.Label('Resi :', className='label-cekresi'),
                dbc.Input(id='resi-input',placeholder='Masukkan nomor resi...', type='text'),
                html.Br(),
                dbc.Button('Submit',color='primary', id='submit-cekresi', n_clicks=0),
                html.Hr()
            ]),
        ])
    , id='cekresi-row'
    ),
    
    html.Div(id='table-container-cekresi',children=[
        dbc.Spinner(children=[
            dt.DataTable(
                id='table-cekresi',
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
        ], size='lg',color='primary',type='border',fullscreen=True)
    ]),
    html.Div(id='notif-cekresi', style={'textAlign':'center'})
])

@app.callback(
    [Output('table-cekresi','data'), Output('table-cekresi','columns'), Output('notif-cekresi','children')],
    [Input('submit-cekresi','n_clicks')],
    [State('dropdown-courier-cekresi','value'), State('resi-input','value')]
)
def getInvoiceInfo(n, Kurir, Resi):
    if n == 0:
        return no_update, no_update

    if Kurir == 'TRIADHIPA':
        df_tri = pd.read_sql(query_tri,cnxn)
        columns = [{'name':i,'id':i} for i in df_tri.columns]
        
        desired_redock = df_tri.loc[df_tri['Redock'] == Resi]
        desired_airwaybill = df_tri.loc[df_tri['Airwaybill'] == Resi]
        if desired_redock.empty and desired_airwaybill.empty:
            return no_update, no_update, dbc.Alert('Data not found!', color="danger", dismissable=True, duration=5000)
        else:
            if desired_redock.empty:
                desired_airwaybill['Tanggal'] = pd.to_datetime(desired_airwaybill['Tanggal'], format='%d-%m-%y').dt.strftime('%Y-%m-%d')
                desired_airwaybill['ReceiveTgl'] = pd.to_datetime(desired_airwaybill['ReceiveTgl'], format='%d-%m-%y').dt.strftime('%Y-%m-%d')

                airway = desired_airwaybill.to_dict('records')
                return airway, columns, no_update
            else:
                desired_redock['Tanggal'] = pd.to_datetime(desired_redock['Tanggal'], format='%d-%m-%y').dt.strftime('%Y-%m-%d')
                desired_redock['ReceiveTgl'] = pd.to_datetime(desired_redock['ReceiveTgl'], format='%d-%m-%y').dt.strftime('%Y-%m-%d')
                redock = desired_redock.to_dict('records')
                return redock, columns, no_update
    elif Kurir == 'JNE':
        print('none')
    else:
        return no_update, no_update, no_update

@app.callback(
    Output('dropdown-courier-cekresi','options'),
    [Input('interval-options-cekresi','n_intervals')]
)
def update_options(n):
    
    df_couriers = pd.read_sql(query_couriers, engine)
    couriers = [{'label':x,'value':x} for x in df_couriers['courier_name']]
    return couriers
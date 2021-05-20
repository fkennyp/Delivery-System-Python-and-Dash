import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
import sqlalchemy as alch
import io, flask, base64
from dash.dependencies import Input, Output, State
from datetime import datetime
from flask import send_file
from dash import no_update

from app import app
from apps import login
from modules import navbar, styleTable, addLog

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT trans_id, trans_invoice, trans_shipment, trans_driver, trans_product_type, trans_sent_date, trans_received_date, trans_store, trans_city, trans_amount, trans_status
FROM transactiondelivery;
'''
query2 = '''
SELECT *
FROM transactiondelivery;
'''
query_stores = '''
SELECT store_name, store_city
FROM mstrstores;
'''
query_status = '''
SELECT status_name
FROM mstrstatus
'''
query_driver = '''
SELECT driver_name
FROM mstrdrivers
'''
query_vehicle = '''
SELECT vehicle_name
FROM mstrgroupvehicles
'''
query_products = '''
SELECT product_name
FROM mstrproducttype
'''
notAllColumns = {'trans_id':'ID', 
                 'trans_invoice':'No. Kwitansi',
                 'trans_shipment':'No. Resi',
                 'trans_driver':'Nama Driver', 
                 'trans_product_type':'Tipe Produk',
                 'trans_sent_date':'Tanggal Kirim',
                 'trans_received_date':'Tanggal Terima',
                 'trans_store':'Toko Tujuan',
                 'trans_city':'Kota Tujuan',
                 'trans_amount':'Harga',
                 'trans_status':'Status'}

AllColumns = {'trans_id':'ID',
              'trans_invoice':'No. Kwitansi',
              'trans_shipment':'No. Resi',
              'trans_driver':'Nama Driver',
              'trans_vehicle':'Kendaraan',
              'trans_product_type':'Tipe Produk',
              'trans_sent_date':'Tanggal Kirim',
              'trans_received_date':'Tanggal Terima',
              'trans_store':'Toko Tujuan',
              'trans_city':'Kota Tujuan',
              'trans_amount':'Harga',
              'trans_status':'Status',
              'trans_KM_awal':'KM Awal',
              'trans_KM_akhir':'KM Akhir',
              'trans_date_cr':'Tanggal dibuat',
              'trans_date_up':'Tanggal diperbarui',
              'trans_by_cr':'Dibuat oleh',
              'trans_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'trans_id',
                 'No. Kwitansi':'trans_invoice',
                 'No. Resi':'trans_shipment',
                 'Nama Driver':'trans_driver',
                 'Kendaraan':'trans_vehicle',
                 'Tipe Produk':'trans_product_type',
                 'Tanggal Kirim':'trans_sent_date',
                 'Tanggal Terima':'trans_received_date',
                 'Toko Tujuan':'trans_store',
                 'Kota Tujuan':'trans_city',
                 'Harga':'trans_amount',
                 'Status':'trans_status',
                 'KM Awal':'trans_KM_awal',
                 'KM Akhir':'trans_KM_akhir',
                 'Tanggal dibuat':'trans_date_cr',
                 'Tanggal diperbarui':'trans_date_up',
                 'Dibuat oleh':'trans_by_cr',
                 'Diperbarui oleh':'trans_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)

df_stores = pd.read_sql(query_stores, engine)
stores = [{'label':x, 'value':x} for x in df_stores['store_name'].unique()]
locations = [{'label':y, 'value':y} for y in df_stores['store_city'].unique()]

df_status = pd.read_sql(query_status, engine)
statuses = [{'label':x, 'value':x} for x in df_status['status_name'].unique()]

df_driver = pd.read_sql(query_driver, engine)
drivers = [{'label':x, 'value':x} for x in df_driver['driver_name'].unique()]

df_vehicle = pd.read_sql(query_vehicle, engine)
vehicles = [{'label':x, 'value':x} for x in df_vehicle['vehicle_name'].unique()]

df_product = pd.read_sql(query_products, engine)
products = [{'label':x, 'value':x} for x in df_product['product_name'].unique()]

#------------------TABLE STYLING--------------
styleHeader={
        'backgroundColor':'rgb(200,200,200)',
        'fontWeight':'bold',
    }
styleCell={
    'textAlign':'center',
    'backgroundColor':'rgb(240,240,240)',
    'width':'75px',
    'fontSize':'12pt',

    'height':'auto',
    'whiteSpace':'normal',
}
styleCondition=[
    {'if': {'column_id': 'ID'},
    'width': '25px'},
]
#--------------LAYOUTS----------------------------
transactions_layout = html.Div([
    dcc.Location(id='trans-url',pathname='/transactions'),
    navbar(),


    html.Div(id='table-container-trans', children=[
        html.H1('Transaksi', id='transaction-header'),
        dbc.Row(
            dbc.Col([
                dbc.Label(id='notif-trans')
            ])
        ),
        html.Div(id='button-container-trans',children=[
            html.Button('Lihat',id='view-page-button-trans',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-trans',href='/transactions/add'),id='add-page-button-trans'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-trans',href='/transactions/edit'),id='edit-page-button-trans'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-trans',href=''),id='refresh-page-button-trans'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-trans'),href='/download_excel_trans/'),
            html.A(html.Button('Tandai completed', id='complete-button-trans', n_clicks=0),href='/transactions')    
        ]),
        html.Div(id='table-refresh-trans',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-trans',
                columns=[{'name':i,'id':i} for i in df_renamed.columns],
                data=df_renamed.to_dict('records'),                    
                editable=False,
                filter_action='native',
                row_selectable='single',
                row_deletable=False,
                sort_action='native', #bisa sort / tidak
                sort_mode='single', #1 or multi column
                page_action="native",
                page_current=0, #ada di halaman brp
                page_size=20, #jmlh row per page
                style_table=styleTable(),
                style_cell=styleCell,
                style_header=styleHeader,
                style_cell_conditional=styleCondition,
                export_format='xlsx',
                fixed_rows={'headers': True},
            )
        ])
    ])
])

add_layout = html.Div([
    dcc.Location(id='trans-add-url',pathname='/transactions/add'),
    navbar(),
    html.H1('Tambah Transaksi', id='transaction-header'),
    html.Div(id='button-container-add-trans', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-trans'),
            id='confirm-add-trans',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-trans'),href='/transactions')
    ]),
    dbc.Spinner(children=[

        dbc.Alert('Data berhasil ditambahkan',id='add-notif-trans', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='trans-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nomor Kwitansi', className='trans-add-label'),
                    dbc.Input(placeholder='Masukkan nomor kwitansi...', id='trans-invoice-value'),
                    html.Br(),
                    dbc.Label('Nomor Resi', className='trans-add-label'),
                    dbc.Input(placeholder='Masukkan nomor resi...', id='trans-shipment-value'),
                    html.Br(),
                    dbc.Label('Nama Driver', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-driver-value',
                        options = drivers,
                        searchable=True,
                        placeholder='Pilih nama driver...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Kendaraan', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-vehicle-value',
                        options = vehicles,
                        searchable=True,
                        placeholder='Pilih nama kendaraan...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Tipe Produk', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-product-type-value',
                        options = stores,
                        searchable=True,
                        placeholder='Pilih tipe produk...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Tanggal Kirim', className='trans-add-label'),
                    dcc.DatePickerSingle(
                        id='trans-sent-date-value',
                        min_date_allowed=(2000,1,1),
                        max_date_allowed=(2050,12,31),
                        initial_visible_month= datetime.now(),
                        display_format='YYYY-MM-DD'
                    ),
                    html.Br(),html.Br(),
                    dbc.Label('Tanggal Terima', className='trans-add-label'),
                    dcc.DatePickerSingle(
                        id='trans-received-date-value',
                        min_date_allowed=(2000,1,1),
                        max_date_allowed=(2050,12,31),
                        initial_visible_month= datetime.now(),
                        display_format='YYYY-MM-DD'
                    ),
                    html.Br(),
                    dbc.Label('Toko Tujuan', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-store-value',
                        options = stores,
                        searchable=True,
                        placeholder='Pilih toko tujuan...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Kota Tujuan', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-city-value',
                        options = locations,
                        searchable=True,
                        placeholder='Pilih kota tujuan...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Harga', className='trans-add-label'),
                    dbc.Input(placeholder='Masukkan harga...', id='trans-amount-value'),
                    html.Br(),
                    dbc.Label('Status', className='trans-add-label'),
                    dcc.Dropdown(
                        id='trans-status-value',
                        options = statuses,
                        searchable=True,
                        placeholder='Pilih status...',
                        clearable=True
                    ),
                    html.Br(),
                    dbc.Label('Kilo Meter (KM) awal', className='trans-add-label'),
                    dbc.Input(placeholder='Masukkan KM awal...', id='trans-KM-awal-value'),
                    html.Br(),
                    dbc.Label('Kilo Meter (KM) akhir', className='trans-add-label'),
                    dbc.Input(placeholder='Masukkan KM akhir...', id='trans-KM-akhir-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='trans-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='trans-edit-url',pathname='/transactions/edit'),
    navbar(),
    html.H1('Rubah Transaksi', id='transaction-header'),
    html.Div(id='button-container-edit-trans',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-trans'),
            id='confirm-edit-trans',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-trans',n_clicks=0),href='/transactions'),
        html.Button(id='refresh-button-edit-trans',n_clicks=0)
    ]),
    dbc.Spinner(children=[

        dbc.Alert('Data berhasil diubah',id='edit-notif-trans', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-trans',children=[
            dt.DataTable(
                id='data-table-edit-trans',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'No. Kwitansi', 'id':'No. Kwitansi', 'editable': True},
                    {'name':'No. Resi', 'id':'No. Resi', 'editable': True},
                    {'name':'Nama Driver', 'id':'Nama Driver', 'editable': True},
                    {'name':'Kendaraan', 'id':'Kendaraan', 'editable': True},
                    {'name':'Tipe Produk', 'id':'Tipe Produk', 'editable': True},
                    {'name':'Tanggal Kirim', 'id':'Tanggal Kirim', 'editable': True},
                    {'name':'Tanggal Terima', 'id':'Tanggal Terima', 'editable': True},
                    {'name':'Toko Tujuan', 'id':'Toko Tujuan', 'editable': True},
                    {'name':'Kota Tujuan', 'id':'Kota Tujuan', 'editable': True},
                    {'name':'Harga', 'id':'Harga', 'editable': True},
                    {'name':'Status', 'id':'Status', 'editable': True},
                    {'name':'KM Awal', 'id':'KM Awal', 'editable': True},
                    {'name':'KM Akhir', 'id':'KM Akhir', 'editable': True},
                    {'name':'Tanggal dibuat', 'id':'Tanggal dibuat', 'editable': False},
                    {'name':'Tanggal diperbarui', 'id':'Tanggal diperbarui', 'editable': False},
                    {'name':'Dibuat oleh', 'id':'Dibuat oleh', 'editable': False},
                    {'name':'Diperbarui oleh', 'id':'Diperbarui oleh', 'editable': False},
                ],
                filter_action='native',
                row_deletable=False,
                page_action="native",
                page_current=0,
                page_size=20,
                style_table=styleTable(),
                style_cell=styleCell,
                style_header=styleHeader,
                style_cell_conditional=styleCondition,
                fixed_rows={'headers': True},
            )
        ])
    ], size='lg', type='grow', fullscreen=True, color='danger')
])



#------------FUNCTIONS---------------
#-------ADD-------
@app.callback(
    [Output('add-notif-trans','is_open')]+\
        [Output('trans-'+x+'-value','options') for x in ['store','city','status','driver','vehicle','product-type']]+\
            [Output('trans-'+x+'-value','invalid') for x in ['invoice','shipment','driver','vehicle','product-type','store','city','amount','status','KM-awal','KM-akhir']]+\
                [Output('trans-notice','children')],
    [Input('confirm-add-trans','submit_n_clicks')],
    [State('trans-'+x+'-value','value') for x in ['invoice','shipment','driver','vehicle','product-type','store','city','amount','status','KM-awal','KM-akhir']]+\
        [State('trans-'+x+'-date-value', 'date') for x in ['sent','received']]
)
def addTrans(n, transInvo, transShip, transDriv, transVehi, transPrType, transStore, transCity, transAmount, transStatus, transKMawal, transKMakhir, transKirim, transTerima):
    df_stores = pd.read_sql(query_stores, engine)
    stores = [{'label':x, 'value':x} for x in df_stores['store_name'].unique()]
    locations = [{'label':y, 'value':y} for y in df_stores['store_city'].unique()]
    df_status = pd.read_sql(query_status, engine)
    statuses = [{'label':x, 'value':x} for x in df_status['status_name'].unique()]
    df_driver = pd.read_sql(query_driver, engine)
    drivers = [{'label':x, 'value':x} for x in df_driver['driver_name'].unique()]
    df_vehicle = pd.read_sql(query_vehicle, engine)
    vehicles = [{'label':x, 'value':x} for x in df_vehicle['vehicle_name'].unique()]
    df_product = pd.read_sql(query_products, engine)
    products = [{'label':x, 'value':x} for x in df_product['product_name'].unique()]
    if not n:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, False, False, False, False, False, ''
    #------------VALIDATION-------------
    if not transInvo:
        return False, stores, locations, statuses, drivers, vehicles, products, True, False, False, False, False, False, False, False, False, False, False, 'Nomor kwitansi belum diisi!'
    elif not transShip:
        return False, stores, locations, statuses, drivers, vehicles, products, False, True, False, False, False, False, False, False, False, False, False, 'Nomor resi belum diisi!'
    elif not transDriv:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, True, False, False, False, False, False, False, False, False, 'Nama driver belum diisi!'
    elif not transVehi:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, True, False, False, False, False, False, False, False, 'Nama kendaraan belum diisi!'
    elif not transPrType:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, True, False, False, False, False, False, False, 'Tipe produk belum diisi!'
    elif not transStore:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, True, False, False, False, False, False, 'Toko tujuan belum diisi!'
    elif not transCity:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, True, False, False, False, False, 'Kota tujuan belum diisi!'
    elif not transAmount:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, False, True, False, False, False, 'Harga belum diisi!'
    elif not transStatus:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, False, False, True, False, False, 'Status belum diisi!'
    elif not transKMawal:
        return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, False, False, False, True, False, 'KM awal belum diisi!'
   


    #------------INPUT PROCESS----------
    else:
        store_choosen = df_stores.loc[df_stores['store_name'] == transStore]
        store_city = store_choosen['store_city']
        
        if not store_city.str.contains(transCity).any():
            return False, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, True, False, False, False, False, 'Toko tersebut tidak terletak di kota tersebut!'
        minute = datetime.now().strftime(' %H:%M:%S')
        sentDate = transKirim + minute
        receivedDate = transTerima + minute

        sentDate_datetime = datetime.strptime(sentDate, '%Y-%m-%d %H:%M:%S')
        receivedDate_datetime = datetime.strptime(receivedDate, '%Y-%m-%d %H:%M:%S')

        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['trans_id'] = str(uuid.uuid4())
        add_df_final['trans_invoice'] = transInvo
        add_df_final['trans_shipment'] = transShip
        add_df_final['trans_driver'] = transDriv
        add_df_final['trans_vehicle'] = transVehi
        add_df_final['trans_product_type'] = transPrType
        add_df_final['trans_sent_date'] = sentDate_datetime
        add_df_final['trans_received_date'] = receivedDate_datetime
        add_df_final['trans_store'] = transStore
        add_df_final['trans_city'] = transCity
        add_df_final['trans_amount'] = transAmount
        add_df_final['trans_status'] = transStatus
        add_df_final['trans_KM_awal'] = transKMawal
        add_df_final['trans_KM_akhir'] = transKMakhir
        add_df_final['trans_date_cr'] = datetime.now()
        add_df_final['trans_date_up'] = datetime.now()
        add_df_final['trans_by_cr'] = login_name
        add_df_final['trans_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'transactiondelivery'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'trans_id': alch.CHAR(36),
                'trans_invoice': alch.VARCHAR(30),
                'trans_shipment': alch.VARCHAR(30),
                'trans_driver': alch.VARCHAR(100),
                'trans_vehicle': alch.VARCHAR(50),
                'trans_product_type': alch.VARCHAR(50),
                'trans_sent_date': alch.DATETIME(),
                'trans_received_date': alch.DATETIME(),
                'trans_store': alch.VARCHAR(55),
                'trans_city': alch.VARCHAR(55),
                'trans_amount': alch.INTEGER(),
                'trans_status': alch.VARCHAR(30),
                'trans_KM_awal': alch.INTEGER(),
                'trans_KM_akhir': alch.INTEGER(),
                'trans_date_cr': alch.DATETIME(),
                'trans_date_up': alch.DATETIME(),
                'trans_by_cr': alch.VARCHAR(50),
                'trans_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE transactiondelivery ADD PRIMARY KEY (trans_id);')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_invoice varchar(30) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_shipment varchar(30) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_driver varchar(100) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_vehicle varchar(50) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_product_type varchar(50) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_sent_date DATETIME NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_received_date DATETIME NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_store varchar(55) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_city varchar(55) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_amount INTEGER NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_status varchar(30) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_up varchar(50) NOT NULL;')
            
        addLog('Transaction','Add')
        return True, stores, locations, statuses, drivers, vehicles, products, False, False, False, False, False, False, False, False, False, False, False, ''

#----EDIT----
@app.callback(
    Output('edit-notif-trans','is_open'),
    [Input('confirm-edit-trans','submit_n_clicks')],
    [State('data-table-edit-trans','data')]
)
def editTrans(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_table[['Tanggal Kirim', 'Tanggal Terima']] = df_table[['Tanggal Kirim', 'Tanggal Terima']].astype('datetime64[ns]')

    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)
    df_table.loc[(df_original_renamed["No. Kwitansi"] != df_table["No. Kwitansi"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["No. Resi"] != df_table["No. Resi"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nama Driver"] != df_table["Nama Driver"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Kendaraan"] != df_table["Kendaraan"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tipe Produk"] != df_table["Tipe Produk"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tanggal Kirim"] < df_table["Tanggal Kirim"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tanggal Terima"] < df_table["Tanggal Terima"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Toko Tujuan"] != df_table["Toko Tujuan"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Kota Tujuan"] != df_table["Kota Tujuan"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Harga"] != df_table["Harga"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Status"] != df_table["Status"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["KM Awal"] != df_table["KM Awal"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["KM Akhir"] != df_table["KM Akhir"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["No. Kwitansi"] != df_table["No. Kwitansi"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["No. Resi"] != df_table["No. Resi"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nama Driver"] != df_table["Nama Driver"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Kendaraan"] != df_table["Kendaraan"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tipe Produk"] != df_table["Tipe Produk"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tanggal Kirim"] < df_table["Tanggal Kirim"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tanggal Terima"] < df_table["Tanggal Terima"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Toko Tujuan"] != df_table["Toko Tujuan"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Kota Tujuan"] != df_table["Kota Tujuan"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Harga"] != df_table["Harga"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Status"] != df_table["Status"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["KM Awal"] != df_table["KM Awal"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["KM Akhir"] != df_table["KM Akhir"]),"Diperbarui oleh"]= login_name

    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'transactiondelivery'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'trans_id': alch.CHAR(36),
            'trans_invoice': alch.VARCHAR(30),
            'trans_shipment': alch.VARCHAR(30),
            'trans_driver': alch.VARCHAR(100),
            'trans_vehicle': alch.VARCHAR(50),
            'trans_product_type': alch.VARCHAR(50),
            'trans_sent_date': alch.DATETIME(),
            'trans_received_date': alch.DATETIME(),
            'trans_store': alch.VARCHAR(55),
            'trans_city': alch.VARCHAR(55),
            'trans_amount': alch.INTEGER(),
            'trans_status': alch.VARCHAR(30),
            'trans_KM_awal': alch.INTEGER(),
            'trans_KM_akhir': alch.INTEGER(),
            'trans_date_cr': alch.DATETIME(),
            'trans_date_up': alch.DATETIME(),
            'trans_by_cr': alch.VARCHAR(50),
            'trans_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE transactiondelivery ADD PRIMARY KEY (trans_id);')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_invoice varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_shipment varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_driver varchar(100) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_vehicle varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_product_type varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_sent_date DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_received_date DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_store varchar(55) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_city varchar(55) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_amount INTEGER NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_status varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_up varchar(50) NOT NULL;')

    addLog('Transaction','Edit')
    return True


#------MARK------
@app.callback(
    Output('data-table-trans','data'),
    [Input('complete-button-trans','n_clicks')],
    [State('data-table-trans','selected_rows'),State('data-table-trans','data')]
)
def markCompleteTrans(n, row, dataset):
    if n == 0:
        return no_update
    str_row = str(row)
    int_row = int(str_row[1:-1])
    data_row = dataset[int_row]
    id_row = data_row['ID']

    read_df = pd.read_sql(query2,engine)
    read_df_renamed = read_df.rename(columns = AllColumns)
    data_selected = read_df_renamed.loc[read_df_renamed['ID'] == id_row]

    data_selected['Status'] = 'COMPLETED'
    
    read_df_renamed.update(data_selected)
    read_df_rev = read_df_renamed.rename(columns = RevAllColumns)
    data_to_table = read_df_rev.to_dict('records')
    
    tab_name = 'transactiondelivery'
    read_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'trans_id': alch.CHAR(36),
            'trans_invoice': alch.VARCHAR(30),
            'trans_shipment': alch.VARCHAR(30),
            'trans_driver': alch.VARCHAR(100),
            'trans_vehicle': alch.VARCHAR(50),
            'trans_product_type': alch.VARCHAR(50),
            'trans_sent_date': alch.DATETIME(),
            'trans_received_date': alch.DATETIME(),
            'trans_store': alch.VARCHAR(55),
            'trans_city': alch.VARCHAR(55),
            'trans_amount': alch.INTEGER(),
            'trans_status': alch.VARCHAR(30),
            'trans_KM_awal': alch.INTEGER(),
            'trans_KM_akhir': alch.INTEGER(),
            'trans_date_cr': alch.DATETIME(),
            'trans_date_up': alch.DATETIME(),
            'trans_by_cr': alch.VARCHAR(50),
            'trans_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE transactiondelivery ADD PRIMARY KEY (trans_id);')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_invoice varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_shipment varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_driver varchar(100) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_vehicle varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_product_type varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_sent_date DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_received_date DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_store varchar(55) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_city varchar(55) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_amount INTEGER NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_status varchar(30) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE transactiondelivery MODIFY trans_by_up varchar(50) NOT NULL;')

    return data_to_table
                

#-----OTHERS-----
@app.callback(
    Output('table-container-trans','children'),
    [Input('view-page-button-trans','n_clicks')],
    [State('data-table-trans','selected_rows'),State('data-table-trans','data')]
)
def viewTrans(n, row_number, dataset):
    if n == 0:
        return no_update
    str_row = str(row_number) #[1] list type
    int_row = int(str_row[1:-1]) #slice the string
    data_row = dataset[int_row] #get the data from list of dataset
    id_row = data_row['ID'] #get the ID
    df5 = pd.read_sql(query2,engine)
    df5_renamed = df5.rename(columns = AllColumns)
    full_dataset = df5_renamed.to_dict('records') 
    desire_data = [d for d in full_dataset if d['ID']==id_row] #get full data

    desire_data_df = pd.DataFrame(desire_data)
    desire_data_df['Tanggal dibuat'] = pd.to_datetime(desire_data_df['Tanggal dibuat']).dt.strftime('%d-%m-%Y %H:%M:%S')
    desire_data_df['Tanggal diperbarui'] = pd.to_datetime(desire_data_df['Tanggal diperbarui']).dt.strftime('%d-%m-%Y %H:%M:%S')
    desire_data_df['Tanggal Kirim'] = pd.to_datetime(desire_data_df['Tanggal Kirim']).dt.strftime('%d-%m-%Y %H:%M:%S')
    desire_data_df['Tanggal Terima'] = pd.to_datetime(desire_data_df['Tanggal Terima']).dt.strftime('%d-%m-%Y %H:%M:%S')

    viewID = desire_data_df.iloc[0][0]
    viewInvo = desire_data_df.iloc[0][1]
    viewShipNum = desire_data_df.iloc[0][2]
    viewDriver = desire_data_df.iloc[0][3]
    viewVehicle = desire_data_df.iloc[0][4]
    viewProdType = desire_data_df.iloc[0][5]
    viewSent = desire_data_df.iloc[0][6]
    viewRecei = desire_data_df.iloc[0][7]
    viewStore = desire_data_df.iloc[0][8]
    viewCity = desire_data_df.iloc[0][9]
    viewAmount = desire_data_df.iloc[0][10]
    viewStatus = desire_data_df.iloc[0][11]
    viewKMawal = desire_data_df.iloc[0][12]
    viewKMakhir = desire_data_df.iloc[0][13]
    viewDateCr = desire_data_df.iloc[0][14]
    viewDateUp = desire_data_df.iloc[0][15]
    viewByCr = desire_data_df.iloc[0][16]
    viewByUp = desire_data_df.iloc[0][17]

    return [
        html.H1('Lihat Transaction', id='transaction-header'),
        html.Div(id='button-container-view-trans',children=[
            html.A(html.Button('Kembali', id='back-view-button-trans'),href='/transactions')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-trans'), html.Br(),
                    dbc.Label(viewID,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('No. Kwitansi :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewInvo,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('No. Resi :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewShipNum,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Nama Driver :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewDriver,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Kendaraan :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewVehicle,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Tipe Produk :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewProdType,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Tanggal Kirim :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewSent,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Tanggal Terima :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewRecei,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Toko Tujuan :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewStore,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Kota Tujuan :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewCity,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Harga :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewAmount,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Status :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewStatus,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('KM Awal :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewKMawal,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('KM Akhir :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewKMakhir,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-trans'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-trans'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-trans'),
                    html.Hr(),
                ])
            , id='row-view-trans')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_trans/")
def exportExcelTrans():
    df8 = pd.read_sql(query2, engine)
    df8_renamed = df8.rename(columns = AllColumns)
    df8_renamed.index = df8_renamed.index + 1
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df8_renamed.to_excel(excel_writer, sheet_name="sheet1")
    excel_writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)

    return send_file(strIO, 
                     attachment_filename='transactions.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)


#---refresh table in main page---
@app.callback(
    Output('table-refresh-trans','children'),
    [Input('refresh-page-button-trans','n_clicks')]
)
def refTrans(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    df3_renamed['Harga'] = df3_renamed.apply(lambda x: "{:,}".format(x['Harga']), axis=1)
    df3_renamed['Tanggal Kirim'] = pd.to_datetime(df3_renamed['Tanggal Kirim']).dt.strftime('%d-%m-%Y %H:%M:%S')
    df3_renamed['Tanggal Terima'] = pd.to_datetime(df3_renamed['Tanggal Terima']).dt.strftime('%d-%m-%Y %H:%M:%S')
    return [
        dt.DataTable(
            id='data-table-trans',
            columns=[{'name':i,'id':i} for i in df3_renamed.columns],
            data=df3_renamed.to_dict('records'),
            editable=False,
            filter_action='native',
            row_selectable='single',
            row_deletable=False,
            sort_action='native', 
            sort_mode='single', 
            page_action="native",
            page_current=0,
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell,
            style_header=styleHeader,
            style_cell_conditional=styleCondition,
            fixed_rows={'headers': True},
        )
    ]

#---refresh table edit page---
@app.callback(
    Output('table-container-edit-trans','children'),
    [Input('refresh-button-edit-trans','n_clicks')]
)
def refEditTrans(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-trans',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'No. Kwitansi', 'id':'No. Kwitansi', 'editable': True},
                {'name':'No. Resi', 'id':'No. Resi', 'editable': True},
                {'name':'Nama Driver', 'id':'Nama Driver', 'editable': True},
                {'name':'Kendaraan', 'id':'Kendaraan', 'editable': True},
                {'name':'Tipe Produk', 'id':'Tipe Produk', 'editable': True},
                {'name':'Tanggal Kirim', 'id':'Tanggal Kirim', 'editable': True},
                {'name':'Tanggal Terima', 'id':'Tanggal Terima', 'editable': True},
                {'name':'Toko Tujuan', 'id':'Toko Tujuan', 'editable': True},
                {'name':'Kota Tujuan', 'id':'Kota Tujuan', 'editable': True},
                {'name':'Harga', 'id':'Harga', 'editable': True},
                {'name':'Status', 'id':'Status', 'editable': True},
                {'name':'KM Awal', 'id':'KM Awal', 'editable': True},
                {'name':'KM Akhir', 'id':'KM Akhir', 'editable': True},
                {'name':'Tanggal dibuat', 'id':'Tanggal dibuat', 'editable': False},
                {'name':'Tanggal diperbarui', 'id':'Tanggal diperbarui', 'editable': False},
                {'name':'Dibuat oleh', 'id':'Dibuat oleh', 'editable': True},
                {'name':'Diperbarui oleh', 'id':'Diperbarui oleh', 'editable': True}
            ],
            data=df5_renamed.to_dict('records'),
            filter_action='native',
            row_deletable=False,
            page_action="native",
            page_current=0, 
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell,
            style_header=styleHeader,
            style_cell_conditional=styleCondition,
            fixed_rows={'headers': True},
        )
    ]

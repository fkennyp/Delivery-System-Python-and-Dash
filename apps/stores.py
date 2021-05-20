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
from modules import navbar, styleTable, styleCell, styleHeader, addLog

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT store_id, store_code, store_name, store_city 
FROM mstrstores
ORDER BY store_code
'''
query2 = '''
SELECT *
FROM mstrstores
ORDER BY store_code
'''
query_trans = '''
SELECT trans_store
FROM transactiondelivery
'''
notAllColumns = {'store_id':'ID', 'store_code':'Kode Toko', 'store_name':'Nama Toko', 'store_city':'Lokasi Toko'}

AllColumns = {'store_id':'ID',
              'store_code':'Kode Toko',
              'store_name':'Nama Toko',
              'store_city':'Lokasi Toko',
              'store_date_cr':'Tanggal dibuat',
              'store_date_up':'Tanggal diperbarui',
              'store_by_cr':'Dibuat oleh',
              'store_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'store_id',
                 'Kode Toko':'store_code',
                 'Nama Toko':'store_name',
                 'Lokasi Toko':'store_city',
                 'Tanggal dibuat':'store_date_cr',
                 'Tanggal diperbarui':'store_date_up',
                 'Dibuat oleh':'store_by_cr',
                 'Diperbarui oleh':'store_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns )
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'store_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
store_layout = html.Div([
    dcc.Location(id='stores-url',pathname='/stores'),
    navbar(),
    html.Div(id='table-container-stores', children=[
        html.H1('Toko', id='store-header'),
        html.Div(id='button-container-stores',children=[
            html.Button('Lihat',id='view-page-button-stores',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-stores',href='/stores/add'),id='add-page-button-stores'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-stores',href='/stores/edit'),id='edit-page-button-stores'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-stores',href='/stores/delete'),id='delete-page-button-stores'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-stores',href=''),id='refresh-page-button-stores'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-stores'),href='/download_excel_stores/'),
        ]),
        html.Div(id='table-refresh-stores',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-stores',
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
                style_cell=styleCell(),
                style_header=styleHeader(),
                style_cell_conditional=styleCondition,
                export_format='xlsx',
                fixed_rows={'headers': True},
            )
        ])
    ])
])

add_layout = html.Div([
    dcc.Location(id='stores-add-url',pathname='/stores/add'),
    navbar(),
    html.H1('Tambah Toko', id='store-header'),
    html.Div(id='button-container-add-stores', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-stores'),
            id='confirm-add-stores',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-stores'),href='/stores')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-stores', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='stores-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Kode', className='stores-add-label'),
                    dbc.Input(placeholder='Masukkan kode toko...', id='stores-code-value'),
                    html.Br(),
                    dbc.Label('Nama', className='stores-add-label'),
                    dbc.Input(placeholder='Masukkan nama toko...', id='stores-name-value'),
                    html.Br(),
                    dbc.Label('Lokasi', className='stores-add-label'),
                    dbc.Input(placeholder='Masukkan lokasi toko...', id='stores-city-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='stores-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='stores-edit-url',pathname='/stores/edit'),
    navbar(),
    html.H1('Rubah Toko', id='store-header'),
    html.Div(id='button-container-edit-stores',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-stores'),
            id='confirm-edit-stores',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-stores',n_clicks=0),href='/stores'),
        html.Button(id='refresh-button-edit-stores',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-stores', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-stores',children=[
            dt.DataTable(
                id='data-table-edit-stores',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Kode Toko', 'id':'Kode Toko', 'editable': True},
                    {'name':'Nama Toko', 'id':'Nama Toko', 'editable': True},
                    {'name':'Lokasi Toko', 'id':'Lokasi Toko', 'editable': True},
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
                style_cell=styleCell(),
                style_header=styleHeader(),
                style_cell_conditional=styleCondition,
                fixed_rows={'headers': True},
            )
        ])
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

delete_layout = html.Div([
    dcc.Location(id='stores-del-url',pathname='/stores/delete'),
    navbar(),
    html.H1('Hapus Store', id='store-header'),
    html.Div(id='button-container-del-stores',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-stores'),
            id='confirm-del-stores',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-stores',n_clicks=0),href='/stores'),
        html.Button(id='refresh-button-del-stores',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert(id='del-notif-stores', is_open=False, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        html.Div(id='table-container-del-stores', children=[
            dt.DataTable(
                id='data-table-del-stores',
                columns=[{'name':i,'id':i} for i in df2_renamed.columns],
                data=df2_renamed.to_dict('records'),
                filter_action='native',
                editable=False,
                row_deletable=True,
                page_action="native",
                page_current=0,
                page_size=20,
                style_table=styleTable(),
                style_cell=styleCell(),
                style_header=styleHeader(),
                style_cell_conditional=styleCondition,
                fixed_rows={'headers': True},
            )
        ])
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

#------------FUNCTIONS---------------

#--------DELETE------
@app.callback(
    [Output('del-notif-stores','is_open'), Output('del-notif-stores','children'), Output('del-notif-stores','color'), Output('del-button-stores','disabled')],
    [Input('confirm-del-stores','submit_n_clicks')],
    [State('data-table-del-stores','data')]
)
def delStores(n, dataset):
    if not n:
        return False

    df_trans = pd.read_sql(query_trans, engine)
    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)

    df_trans2 = df_trans.drop_duplicates(subset=['trans_store'])
    df_checker = df_trans2.assign(result=df_trans2['trans_store'].isin(deleted_df_rev['store_name']).astype(int))
    

    if 0 in df_checker.values: 
        return True,'Anda tidak bisa menghapus toko yang masih berada di transaction!\nSilahkan refresh kembali page ini.','danger', 'True'
    else:
        tab_name = 'mstrstores'
        deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'store_id': alch.CHAR(36),
                'store_code': alch.VARCHAR(25),
                'store_name': alch.VARCHAR(50),
                'store_city': alch.VARCHAR(50),
                'store_date_cr': alch.DATETIME(),
                'store_date_up': alch.DATETIME(),
                'store_by_cr': alch.VARCHAR(50),
                'store_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrstores ADD PRIMARY KEY (store_id);')
            con.execute('ALTER TABLE mstrstores MODIFY store_code varchar(25) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_city varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_by_up varchar(50) NOT NULL;')
            
        addLog('Stores','Delete')
        return True, 'Data berhasil dihapus', 'success', no_update

@app.callback(
    Output('table-container-del-stores','children'),
    [Input('refresh-button-del-stores','n_clicks')]
)
def refDelStores(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-stores',
            columns=[{'name':i,'id':i} for i in df6_renamed.columns],
            data=df6_renamed.to_dict('records'),
            editable=False,
            filter_action='native',
            row_deletable=True,
            page_action="native",
            page_current=0,
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell(),
            style_header=styleHeader(),
            style_cell_conditional=styleCondition,
            fixed_rows={'headers': True},
        )
    ]

#------ADD-----
@app.callback(
    [Output('add-notif-stores','is_open')]+\
        [Output('stores-'+x+'-value','invalid') for x in ['code','name','city']]+\
            [Output('stores-notice','children')],
    [Input('confirm-add-stores','submit_n_clicks')],
    [State('stores-'+x+'-value','value') for x in ['code','name','city']]
)
def addStores(n, storeCode, storeName, storeCity):
    if not n:
        return False, False, False, False, ''

    if not storeCode:
        return False, True, False, False, 'Kode toko belum diisi!'
    elif not storeName:
        return False, False, True, False, 'Nama toko belum diisi!'
    elif not storeCity:
        return False, False, False, True, 'Lokasi toko belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['store_id'] = str(uuid.uuid4())
        add_df_final['store_code'] = storeCode
        add_df_final['store_name'] = storeName
        add_df_final['store_city'] = storeCity
        add_df_final['store_date_cr'] = datetime.now()
        add_df_final['store_date_up'] = datetime.now()
        add_df_final['store_by_cr'] = login_name
        add_df_final['store_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrstores'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'store_id': alch.CHAR(36),
                'store_code': alch.VARCHAR(25),
                'store_name': alch.VARCHAR(50),
                'store_city': alch.VARCHAR(50),
                'store_date_cr': alch.DATETIME(),
                'store_date_up': alch.DATETIME(),
                'store_by_cr': alch.VARCHAR(50),
                'store_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrstores ADD PRIMARY KEY (store_id);')
            con.execute('ALTER TABLE mstrstores MODIFY store_code varchar(25) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_city varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstores MODIFY store_by_up varchar(50) NOT NULL;')

        addLog('Stores','Add')
        return True, False, False, False, ''

#----------EDIT---------
@app.callback(
    Output('edit-notif-stores','is_open'),
    [Input('confirm-edit-stores','submit_n_clicks')],
    [State('data-table-edit-stores','data')]
)
def editStores(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Kode Toko"] != df_table["Kode Toko"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nama Toko"] != df_table["Nama Toko"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Lokasi Toko"] != df_table["Lokasi Toko"]),"Tanggal diperbarui"]=datetime.now()

    df_table.loc[(df_original_renamed["Kode Toko"] != df_table["Kode Toko"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nama Toko"] != df_table["Nama Toko"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Lokasi Toko"] != df_table["Lokasi Toko"]),"Diperbarui oleh"]= login_name

    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrstores'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'store_id': alch.CHAR(36),
            'store_code': alch.VARCHAR(25),
            'store_name': alch.VARCHAR(50),
            'store_city': alch.VARCHAR(50),
            'store_date_cr': alch.DATETIME(),
            'store_date_up': alch.DATETIME(),
            'store_by_cr': alch.VARCHAR(50),
            'store_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrstores ADD PRIMARY KEY (store_id);')
        con.execute('ALTER TABLE mstrstores MODIFY store_code varchar(25) NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_city varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrstores MODIFY store_by_up varchar(50) NOT NULL;')

    addLog('Stores','Edit')
    return True

@app.callback(
    Output('table-container-edit-stores','children'),
    [Input('refresh-button-edit-stores','n_clicks')]
)
def refEditStores(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-stores',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Kode Toko', 'id':'Kode Toko', 'editable': True},
                {'name':'Nama Toko', 'id':'Nama Toko', 'editable': True},
                {'name':'Lokasi Toko', 'id':'Lokasi Toko', 'editable': True},
                {'name':'Tanggal dibuat', 'id':'Tanggal dibuat', 'editable': False},
                {'name':'Tanggal diperbarui', 'id':'Tanggal diperbarui', 'editable': False},
                {'name':'Dibuat oleh', 'id':'Dibuat oleh', 'editable': False},
                {'name':'Diperbarui oleh', 'id':'Diperbarui oleh', 'editable': False},
            ],
            data=df5_renamed.to_dict('records'),
            filter_action='native',
            row_deletable=False,
            page_action="native",
            page_current=0, 
            page_size=20,
            style_table=styleTable(),
            style_cell=styleCell(),
            style_header=styleHeader(),
            style_cell_conditional=styleCondition,
            fixed_rows={'headers': True},
        )
    ]

@app.callback(
    Output('table-refresh-stores','children'),
    [Input('refresh-page-button-stores','n_clicks')]
)
def refEdit(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-stores',
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
            style_cell=styleCell(),
            style_header=styleHeader(),
            style_cell_conditional=styleCondition,
            fixed_rows={'headers': True},
        )
    ]
                
@app.callback(
    Output('table-container-stores','children'),
    [Input('view-page-button-stores','n_clicks')],
    [State('data-table-stores','selected_rows'),State('data-table-stores','data')]
)
def viewStores(n, row_number, dataset):
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

    viewID = desire_data_df.iloc[0][0]
    viewCode = desire_data_df.iloc[0][1]
    viewName = desire_data_df.iloc[0][2]
    viewCity = desire_data_df.iloc[0][3]
    viewDateCr = desire_data_df.iloc[0][4]
    viewDateUp = desire_data_df.iloc[0][5]
    viewByCr = desire_data_df.iloc[0][6]
    viewByUp = desire_data_df.iloc[0][7]

    return [
        html.H1('Lihat Toko', id='menu-header'),
        html.Div(id='button-container-view-stores',children=[
            html.A(html.Button('Kembali', id='back-view-button-stores'),href='/stores')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-stores'), html.Br(),
                    dbc.Label(viewID,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Kode Toko :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewCode,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Nama Toko :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewName,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Lokasi Toko :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewCity,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-stores'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-stores'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-stores'),
                    html.Hr(),
                ])
            , id='row-view-stores')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_stores/")
def exportExcelStores():
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
                     attachment_filename='stores.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
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
from modules import navbar, styleHeader, styleCell, styleTable, addLog

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT product_id, product_name, product_type, product_description 
FROM mstrproducttype;
'''
query2 = '''
SELECT *
FROM mstrproducttype;
'''
query_trans = '''
SELECT trans_product_type
FROM transactiondelivery
'''
notAllColumns = {'product_id':'ID', 'product_name':'Nama Produk', 'product_type':'Tipe Produk', 'product_description':'Deskripsi'}

AllColumns = {'product_id':'ID',
              'product_name':'Nama Produk',
              'product_type':'Tipe Produk',
              'product_description':'Deskripsi',
              'product_date_cr':'Tanggal dibuat',
              'product_date_up':'Tanggal diperbarui',
              'product_by_cr':'Dibuat oleh',
              'product_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'product_id',
                 'Nama Produk':'product_name',
                 'Tipe Produk':'product_type',
                 'Deskripsi':'product_description',
                 'Tanggal dibuat':'product_date_cr',
                 'Tanggal diperbarui':'product_date_up',
                 'Dibuat oleh':'product_by_cr',
                 'Diperbarui oleh':'product_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'product_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
products_layout = html.Div([
    dcc.Location(id='prods-url',pathname='/products'),
    navbar(),
    html.Div(id='table-container-prods', children=[
        html.H1('Produk', id='product-header'),
        html.Div(id='button-container-prods',children=[
            html.Button('Lihat',id='view-page-button-prods',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-prods',href='/products/add'),id='add-page-button-prods'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-prods',href='/products/edit'),id='edit-page-button-prods'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-prods',href='/products/delete'),id='delete-page-button-prods'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-prods',href=''),id='refresh-page-button-prods'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-prods'),href='/download_excel_prods/'),
        ]),
        html.Div(id='table-refresh-prods',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-prods',
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
    dcc.Location(id='prods-add-url',pathname='/products/add'),
    navbar(),
    html.H1('Tambah Produk', id='product-header'),
    html.Div(id='button-container-add-prods', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-prods'),
            id='confirm-add-prods',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-prods'),href='/products')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-prods', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='prods-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='prods-add-label'),
                    dbc.Input(placeholder='Masukkan nama produk...', id='prods-name-value'),
                    html.Br(),
                    dbc.Label('Tipe', className='prods-add-label'),
                    dbc.Input(placeholder='Masukkan tipe produk...', id='prods-type-value'),
                    html.Br(),
                    dbc.Label('Deskripsi', className='prods-add-label'),
                    dbc.Input(placeholder='Masukkan deskripsi produk...', id='prods-description-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='prods-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='prods-edit-url',pathname='/products/edit'),
    navbar(),
    html.H1('Rubah Produk', id='product-header'),
    html.Div(id='button-container-edit-prods',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-prods'),
            id='confirm-edit-prods',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-prods',n_clicks=0),href='/products'),
        html.Button(id='refresh-button-edit-prods',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-prods', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-prods',children=[
            dt.DataTable(
                id='data-table-edit-prods',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Produk', 'id':'Nama Produk', 'editable': True},
                    {'name':'Tipe Produk', 'id':'Tipe Produk', 'editable': True},
                    {'name':'Deskripsi', 'id':'Deskripsi', 'editable': True},
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
    dcc.Location(id='prods-del-url',pathname='/products/delete'),
    navbar(),
    html.H1('Hapus Produk', id='product-header'),
    html.Div(id='button-container-del-prods',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-prods'),
            id='confirm-del-prods',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-prods',n_clicks=0),href='/products'),
        html.Button(id='refresh-button-del-prods',n_clicks=0)
    ]),
    dbc.Spinner([
        dbc.Alert(id='del-notif-prods', is_open=False, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-prods', children=[
            dt.DataTable(
                id='data-table-del-prods',
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

#------DELETE-----
@app.callback(
    [Output('del-notif-prods','is_open'), Output('del-notif-prods','children'), Output('del-notif-prods','color'), Output('del-button-prods','disabled')],
    [Input('confirm-del-prods','submit_n_clicks')],
    [State('data-table-del-prods','data')]
)
def delProduct(n, dataset):
    if not n:
        return False

    df_trans = pd.read_sql(query_trans, engine)
    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    
    df_trans2 = df_trans.drop_duplicates(subset=['trans_product_type'])
    df_checker = df_trans2.assign(result=df_trans2['trans_product_type'].isin(deleted_df_rev['product_name']).astype(int))

    if 0 in df_checker.values: 
        return True,'Anda tidak bisa menghapus produk yang masih berada di transaction!\nSilahkan refresh kembali page ini.','danger', 'True'
    else:
        tab_name = 'mstrproducttype'
        deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'product_id': alch.CHAR(36),
                'product_name': alch.VARCHAR(100),
                'product_type': alch.VARCHAR(50),
                'product_description': alch.VARCHAR(300),
                'product_date_cr': alch.DATETIME(),
                'product_date_up': alch.DATETIME(),
                'product_by_cr': alch.VARCHAR(50),
                'product_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrproducttype ADD PRIMARY KEY (product_id);')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_name varchar(100) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_type varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_description varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_by_up varchar(50) NOT NULL;')

        addLog('Products','Delete')
        return True, 'Data berhasil dihapus', 'success', no_update

@app.callback(
    Output('table-container-del-prods','children'),
    [Input('refresh-button-del-prods','n_clicks')]
)
def refDelProduct(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-prods',
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

#------ADD------
@app.callback(
    [Output('add-notif-prods','is_open')]+\
        [Output('prods-'+x+'-value','invalid') for x in ['name','type','description']]+\
            [Output('prods-notice','children')],
    [Input('confirm-add-prods','submit_n_clicks')],
    [State('prods-'+x+'-value','value') for x in ['name','type','description']]
)
def addProduct(n, prodName, prodType, prodDesc):
    if not n:
        return False, False, False, False, ''

    if not prodName:
        return False, True, False, False, 'Nama produk belum diisi!'
    elif not prodType:
        return False, False, True, False, 'Tipe produk belum diisi!'
    elif not prodDesc:
        return False, False, False, True, 'Deskripsi produk belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['product_id'] = str(uuid.uuid4())
        add_df_final['product_name'] = prodName
        add_df_final['product_type'] = prodType
        add_df_final['product_description'] = prodDesc
        add_df_final['product_date_cr'] = datetime.now()
        add_df_final['product_date_up'] = datetime.now()
        add_df_final['product_by_cr'] = login_name
        add_df_final['product_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrproducttype'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'product_id': alch.CHAR(36),
                'product_name': alch.VARCHAR(100),
                'product_type': alch.VARCHAR(50),
                'product_description': alch.VARCHAR(300),
                'product_date_cr': alch.DATETIME(),
                'product_date_up': alch.DATETIME(),
                'product_by_cr': alch.VARCHAR(50),
                'product_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrproducttype ADD PRIMARY KEY (product_id);')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_name varchar(100) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_type varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_description varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrproducttype MODIFY product_by_up varchar(50) NOT NULL;')

        addLog('Products','Add')
        return True, False, False, False, ''

#--------EDIT------
@app.callback(
    Output('edit-notif-prods','is_open'),
    [Input('confirm-edit-prods','submit_n_clicks')],
    [State('data-table-edit-prods','data')]
)
def editProduct(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama Produk"] != df_table["Nama Produk"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tipe Produk"] != df_table["Tipe Produk"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Nama Produk"] != df_table["Nama Produk"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tipe Produk"] != df_table["Tipe Produk"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Diperbarui oleh"]= login_name
    
    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrproducttype'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'product_id': alch.CHAR(36),
            'product_name': alch.VARCHAR(100),
            'product_type': alch.VARCHAR(50),
            'product_description': alch.VARCHAR(300),
            'product_date_cr': alch.DATETIME(),
            'product_date_up': alch.DATETIME(),
            'product_by_cr': alch.VARCHAR(50),
            'product_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrproducttype ADD PRIMARY KEY (product_id);')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_name varchar(100) NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_type varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_description varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrproducttype MODIFY product_by_up varchar(50) NOT NULL;')

    addLog('Products','Edit')
    return True

@app.callback(
    Output('table-container-edit-prods','children'),
    [Input('refresh-button-edit-prods','n_clicks')]
)
def refEditProduct(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-prods',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Produk', 'id':'Nama Produk', 'editable': True},
                {'name':'Tipe Produk', 'id':'Tipe Produk', 'editable': True},
                {'name':'Deskripsi', 'id':'Deskripsi', 'editable': True},
                {'name':'Tanggal dibuat', 'id':'Tanggal dibuat', 'editable': False},
                {'name':'Tanggal diperbarui', 'id':'Tanggal diperbarui', 'editable': False},
                {'name':'Dibuat oleh', 'id':'Dibuat oleh', 'editable': True},
                {'name':'Diperbarui oleh', 'id':'Diperbarui oleh', 'editable': True},
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
    Output('table-refresh-prods','children'),
    [Input('refresh-page-button-prods','n_clicks')]
)
def refProduct(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-prods',
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
    Output('table-container-prods','children'),
    [Input('view-page-button-prods','n_clicks')],
    [State('data-table-prods','selected_rows'),State('data-table-prods','data')]
)
def viewProduct(n, row_number, dataset):
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
    viewName = desire_data_df.iloc[0][1]
    viewType = desire_data_df.iloc[0][2]
    viewDesc = desire_data_df.iloc[0][3]
    viewDateCr = desire_data_df.iloc[0][4]
    viewDateUp = desire_data_df.iloc[0][5]
    viewByCr = desire_data_df.iloc[0][6]
    viewByUp = desire_data_df.iloc[0][7]

    return [
        html.H1('Lihat Product', id='product-header'),
        html.Div(id='button-container-view-prods',children=[
            html.A(html.Button('Kembali', id='back-view-button-prods'),href='/products')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-prods'), html.Br(),
                    dbc.Label(viewID,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewName,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Tipe :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewType,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Deskripsi :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewDesc,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-prods'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-prods'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-prods'),
                    html.Hr(),
                ])
            , id='row-view-prods')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_prods/")
def exportExcelProduct():
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
                     attachment_filename='products.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
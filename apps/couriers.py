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
from modules import navbar, styleCell, styleHeader, styleTable, addLog

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT courier_id, courier_code, courier_name 
FROM mstrcouriers;
'''
query2 = '''
SELECT *
FROM mstrcouriers;
'''
notAllColumns = {'courier_id':'ID', 'courier_code':'Kode Kurir', 'courier_name':'Nama Kurir'}

AllColumns = {'courier_id':'ID',
              'courier_code':'Kode Kurir',
              'courier_name':'Nama Kurir',
              'courier_date_cr':'Tanggal dibuat',
              'courier_date_up':'Tanggal diperbarui',
              'courier_by_cr':'Dibuat oleh',
              'courier_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'courier_id',
                 'Kode Kurir':'courier_code',
                 'Nama Kurir':'courier_name',
                 'Tanggal dibuat':'courier_date_cr',
                 'Tanggal diperbarui':'courier_date_up',
                 'Dibuat oleh':'courier_by_cr',
                 'Diperbarui oleh':'courier_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'courier_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
courier_layout = html.Div([
    dcc.Location(id='courier-url',pathname='/couriers'),
    navbar(),
    html.Div(id='table-container-couriers', children=[
        html.H1('Kurir', id='courier-header'),
        html.Div(id='button-container-couriers',children=[
            html.Button('Lihat',id='view-page-button-couriers',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-couriers',href='/couriers/add'),id='add-page-button-couriers'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-couriers',href='/couriers/edit'),id='edit-page-button-couriers'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-couriers',href='/couriers/delete'),id='delete-page-button-couriers'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-couriers',href='/couriers'),id='refresh-page-button-couriers'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-couriers'),href='/download_excel_couriers/'),
        ]),
        html.Div(id='table-refresh-couriers',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-couriers',
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
                # style_as_list_view=True, #membuat tidak ada garis di antara kolom, true  
                style_cell_conditional=styleCondition,
                export_format='xlsx',
                fixed_rows={'headers': True},
            )
        ])
    ])
])

add_layout = html.Div([
    dcc.Location(id='couriers-add-url',pathname='/couriers/add'),
    navbar(),
    html.H1('Tambah Kurir', id='courier-header'),
    html.Div(id='button-container-add-couriers', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-couriers'),
            id='confirm-add-couriers',
            message='Anda yakin ingin menambahkan data?'
        ),
        html.A(html.Button('Kembali', id='back-add-button-couriers'),href='/couriers')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-couriers', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='couriers-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Kode', className='couriers-add-label'),
                    dbc.Input(placeholder='Masukkan kode kurir...', id='couriers-code-value'),
                    html.Br(),
                    dbc.Label('Nama', className='couriers-add-label'),
                    dbc.Input(placeholder='Masukkan nama kurir...', id='couriers-name-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='couriers-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
    
])

edit_layout = html.Div([
    dcc.Location(id='couriers-edit-url',pathname='/couriers/edit'),
    navbar(),
    html.H1('Rubah Kurir', id='courier-header'),
    html.Div(id='button-container-edit-couriers',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-couriers',n_clicks=0),
            id='confirm-edit-couriers',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-couriers',n_clicks=0),href='/couriers'),
        html.Button(id='refresh-button-edit-couriers',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-couriers', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-couriers',children=[
            dt.DataTable(
                id='data-table-edit-couriers',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Kode Kurir', 'id':'Kode Kurir', 'editable': True},
                    {'name':'Nama Kurir', 'id':'Nama Kurir', 'editable': True},
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
    dcc.Location(id='couriers-del-url',pathname='/couriers/delete'),
    navbar(),
    html.H1('Hapus Kurir', id='courier-header'),
    html.Div(id='button-container-del-couriers',children=[
        dcc.ConfirmDialogProvider(children=    
            html.Button('Kirim', id='del-button-couriers'),
            id='confirm-del-couriers',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali',id='back-del-button-couriers',n_clicks=0),href='/couriers'),
        html.Button(id='refresh-button-del-couriers',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil dihapus',id='del-notif-couriers', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-couriers', children=[
            dt.DataTable(
                id='data-table-del-couriers',
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

#-----DELETE----
@app.callback(
    Output('del-notif-couriers','is_open'),
    [Input('confirm-del-couriers','submit_n_clicks')],
    [State('data-table-del-couriers','data')]
)
def delCourier(n, dataset):
    if not n:
        return False

    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    tab_name = 'mstrcouriers'
    deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'courier_id': alch.CHAR(36),
            'courier_code': alch.VARCHAR(25),
            'courier_name': alch.VARCHAR(50),
            'courier_date_cr': alch.DATETIME(),
            'courier_date_up': alch.DATETIME(),
            'courier_by_cr': alch.VARCHAR(50),
            'courier_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrcouriers ADD PRIMARY KEY (courier_id);')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_code varchar(25) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_up varchar(50) NOT NULL;')

    addLog('Couriers','Delete')
    return True

@app.callback(
    Output('table-container-del-couriers','children'),
    [Input('refresh-button-del-couriers','n_clicks')]
)
def refDelCourier(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-couriers',
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


#----------ADD---------
@app.callback(
    [Output('add-notif-couriers','is_open')]+\
        [Output('couriers-'+x+'-value','invalid') for x in ['code','name']]+\
            [Output('couriers-notice','children')],
    [Input('confirm-add-couriers','submit_n_clicks')],
    [State('couriers-'+x+'-value','value') for x in ['code','name']]
)
def addCourier(n, code, name):
    if not n:
        return False, False, False, ''

    if not code:
        return False, True, False, 'Kode kurir belum diisi!'
    elif not name:
        return False, False, True, 'Nama kurir belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['courier_id'] = str(uuid.uuid4())
        add_df_final['courier_code'] = code
        add_df_final['courier_name'] = name
        add_df_final['courier_date_cr'] = datetime.now()
        add_df_final['courier_date_up'] = datetime.now()
        add_df_final['courier_by_cr'] = login_name
        add_df_final['courier_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)
        
        tab_name = 'mstrcouriers'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'courier_id': alch.CHAR(36),
                'courier_code': alch.VARCHAR(25),
                'courier_name': alch.VARCHAR(50),
                'courier_date_cr': alch.DATETIME(),
                'courier_date_up': alch.DATETIME(),
                'courier_by_cr': alch.VARCHAR(50),
                'courier_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrcouriers ADD PRIMARY KEY (courier_id);')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_code varchar(25) NOT NULL;')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_up varchar(50) NOT NULL;')

        addLog('Couriers', 'Add')
        return True, False, False, ''
    
#------EDIT-----
@app.callback(
    Output('edit-notif-couriers','is_open'),
    [Input('confirm-edit-couriers','submit_n_clicks')],
    [State('data-table-edit-couriers','data')]
)
def editCourier(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Kode Kurir"] != df_table["Kode Kurir"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nama Kurir"] != df_table["Nama Kurir"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Kode Kurir"] != df_table["Kode Kurir"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nama Kurir"] != df_table["Nama Kurir"]),"Diperbarui oleh"]= login_name
    
    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrcouriers'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'courier_id': alch.CHAR(36),
            'courier_code': alch.VARCHAR(25),
            'courier_name': alch.VARCHAR(50),
            'courier_date_cr': alch.DATETIME(),
            'courier_date_up': alch.DATETIME(),
            'courier_by_cr': alch.VARCHAR(50),
            'courier_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrcouriers ADD PRIMARY KEY (courier_id);')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_code varchar(25) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrcouriers MODIFY courier_by_up varchar(50) NOT NULL;')

    addLog('Couriers','Edit')
    return True


@app.callback(
    Output('table-container-edit-couriers','children'),
    [Input('refresh-button-edit-couriers','n_clicks')]
)
def refEditCourier(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-couriers',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Kode Kurir', 'id':'Kode Kurir', 'editable': True},
                {'name':'Nama Kurir', 'id':'Nama Kurir', 'editable': True},
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
    Output('table-refresh-couriers','children'),
    [Input('refresh-page-button-couriers','n_clicks')]
)
def refCourier(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-couriers',
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
    Output('table-container-couriers','children'),
    [Input('view-page-button-couriers','n_clicks')],
    [State('data-table-couriers','selected_rows'),State('data-table-couriers','data')]
)
def viewCourier(n, row_number, dataset):
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
    viewDateCr = desire_data_df.iloc[0][3]
    viewDateUp = desire_data_df.iloc[0][4]
    viewByCr = desire_data_df.iloc[0][5]
    viewByUp = desire_data_df.iloc[0][6]

    return [
        html.H1('Lihat Kurir', id='courier-header'),
        html.Div(id='button-container-view-couriers',children=[
            html.A(html.Button('Kembali', id='back-view-button-couriers'),href='/couriers')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-couriers'), html.Br(),
                    dbc.Label(viewID,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Kode Kurir :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewCode,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewName,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-couriers'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-couriers'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-couriers'),
                    html.Hr(),
                ])
            , id='row-view-couriers')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_couriers/")
def exportExcelCourier():
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
                     attachment_filename='couriers.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
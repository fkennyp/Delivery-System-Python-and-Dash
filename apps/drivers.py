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
SELECT driver_id, driver_name, driver_phone
FROM mstrdrivers;
'''
query2 = '''
SELECT *
FROM mstrdrivers;
'''
query_trans = '''
SELECT trans_driver
FROM transactiondelivery
'''

notAllColumns = {'driver_id':'ID', 'driver_name':'Nama Driver', 'driver_phone':'Nomor HP'}

AllColumns = {'driver_id':'ID',
              'driver_name':'Nama Driver',
              'driver_phone':'Nomor HP',
              'driver_SIM_type':'Tipe SIM',
              'driver_SIM_num':'Nomor SIM',
              'driver_date_cr':'Tanggal dibuat',
              'driver_date_up':'Tanggal diperbarui',
              'driver_by_cr':'Dibuat oleh',
              'driver_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'driver_id',
                 'Nama Driver':'driver_name',
                 'Nomor HP':'driver_phone',
                 'Tipe SIM':'driver_SIM_type',
                 'Nomor SIM':'driver_SIM_num',
                 'Tanggal dibuat':'driver_date_cr',
                 'Tanggal diperbarui':'driver_date_up',
                 'Dibuat oleh':'driver_by_cr',
                 'Diperbarui oleh':'driver_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)

df_trans = pd.read_sql(query_trans, engine)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'ID'},
    'width': '100px'},
    {'if': {'column_id': 'Nama Driver'},
    'width': '100px'}
]
#--------------LAYOUTS----------------------------
drivers_layout = html.Div([
    dcc.Location(id='drivers-url',pathname='/drivers'),
    navbar(),
    html.Div(id='table-container-drivers', children=[
        html.H1('Driver', id='driver-header'),
        html.Div(id='button-container-drivers',children=[
            html.Button('Lihat',id='view-page-button-drivers',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-drivers',href='/drivers/add'),id='add-page-button-drivers'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-drivers',href='/drivers/edit'),id='edit-page-button-drivers'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-drivers',href='/drivers/delete'),id='delete-page-button-drivers'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-drivers',href=''),id='refresh-page-button-drivers'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-drivers'),href='/download_excel_drivers/'),
        ]),
        html.Div(id='table-refresh-drivers',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-drivers',
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
    dcc.Location(id='drivers-add-url',pathname='/drivers/add'),
    navbar(),
    html.H1('Tambah Driver', id='driver-header'),
    html.Div(id='button-container-add-drivers', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-drivers'),
            id='confirm-add-drivers',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-drivers'),href='/drivers')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-drivers', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='drivers-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='drivers-add-label'),
                    dbc.Input(placeholder='Masukkan nama driver...', id='drivers-name-value'),
                    html.Br(),
                    dbc.Label('Nomor HP', className='drivers-add-label'),
                    dbc.Input(placeholder='Masukkan nomor HP...', id='drivers-phone-value'),
                    html.Br(),
                    dbc.Label('Tipe SIM', className='drivers-add-label'),
                    dbc.Input(placeholder='Masukkan tipe SIM... (maksimal 5 karakter)', id='drivers-type-value'),
                    html.Br(),
                    dbc.Label('Nomor SIM', className='drivers-add-label'),
                    dbc.Input(placeholder='Masukkan nomor SIM...', id='drivers-sim-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='drivers-row'),

    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='drivers-edit-url',pathname='/drivers/edit'),
    navbar(),
    html.H1('Rubah Driver', id='driver-header'),
    html.Div(id='button-container-edit-drivers',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-drivers',n_clicks=0),
            id='confirm-edit-drivers',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-drivers',n_clicks=0),href='/drivers'),
        html.Button(id='refresh-button-edit-drivers',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-drivers', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        html.Div(id='table-container-edit-drivers',children=[
            dt.DataTable(
                id='data-table-edit-drivers',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Driver', 'id':'Nama Driver', 'editable': True},
                    {'name':'Nomor HP', 'id':'Nomor HP', 'editable': True},
                    {'name':'Tipe SIM', 'id':'Tipe SIM', 'editable': True},
                    {'name':'Nomor SIM', 'id':'Nomor SIM', 'editable': True},
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
    dcc.Location(id='drivers-del-url',pathname='/drivers/delete'),
    navbar(),
    html.H1('Hapus Driver', id='driver-header'),
    html.Div(id='button-container-del-drivers',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-drivers'),
            id='confirm-del-drivers',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-drivers',n_clicks=0),href='/drivers'),
        html.Button(id='refresh-button-del-drivers',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert(id='del-notif-drivers', is_open=False, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-drivers', children=[
            dt.DataTable(
                id='data-table-del-drivers',
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


#------DELETE------
@app.callback(
    [Output('del-notif-drivers','is_open'), Output('del-notif-drivers','children'), Output('del-notif-drivers','color'), Output('del-button-drivers','disabled')],
    [Input('confirm-del-drivers','submit_n_clicks')],
    [State('data-table-del-drivers','data')]
)
def delDrivers(n, dataset):
    if not n:
        return False

    df_trans = pd.read_sql(query_trans,engine)
    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    
    df_trans2 = df_trans.drop_duplicates(subset=['trans_driver'])
    df_checker = df_trans2.assign(result=df_trans2['trans_driver'].isin(deleted_df_rev['driver_name']).astype(int))

    if 0 in df_checker.values: 
        return True,'Anda tidak bisa menghapus driver yang masih berada di transaction!\nSilahkan refresh kembali page ini.','danger', 'True'
    
    else:
        tab_name = 'mstrdrivers'
        deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'driver_id': alch.CHAR(36),
                'driver_name': alch.VARCHAR(50),
                'driver_phone': alch.VARCHAR(20),
                'driver_SIM_type': alch.VARCHAR(5),
                'driver_SIM_num': alch.VARCHAR(20),
                'driver_date_cr': alch.DATETIME(),
                'driver_date_up': alch.DATETIME(),
                'driver_by_cr': alch.VARCHAR(50),
                'driver_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrdrivers ADD PRIMARY KEY (driver_id);')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_phone varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_type varchar(5) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_num varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_up varchar(50) NOT NULL;')

        addLog('Drivers','Delete')
        return True, 'Data berhasil dihapus', 'success', no_update

@app.callback(
    Output('table-container-del-drivers','children'),
    [Input('refresh-button-del-drivers','n_clicks')]
)
def refDelDrivers(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-drivers',
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

#------ADD-------

@app.callback(
    [Output('add-notif-drivers','is_open')]+\
        [Output('drivers-'+x+'-value','invalid') for x in ['name','phone','type','sim']]+\
            [Output('drivers-notice','children')],
    [Input('confirm-add-drivers','submit_n_clicks')],
    [State('drivers-'+x+'-value','value') for x in ['name','phone','type','sim']]
)
def addDrivers(n, drivName, drivPhone, drivType, drivSim):
    if not n:
        return False, False, False, False, False, ''

    if not drivName:
        return False, True, False, False, False, 'Nama driver belum diisi!'
    elif not drivPhone:
        return False, False, True, False, False, 'Nomor HP belum diisi!'
    elif not drivType:
        return False, False, False, True, False, 'Tipe SIM belum diisi!'
    elif not drivSim:
        return False, False, False, False, True, 'Nomor SIM belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['driver_id'] = str(uuid.uuid4())
        add_df_final['driver_name'] = drivName
        add_df_final['driver_phone'] = drivPhone
        add_df_final['driver_SIM_type'] = drivType
        add_df_final['driver_SIM_num'] = drivSim
        add_df_final['driver_date_cr'] = datetime.now()
        add_df_final['driver_date_up'] = datetime.now()
        add_df_final['driver_by_cr'] = login_name
        add_df_final['driver_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrdrivers'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'driver_id': alch.CHAR(36),
                'driver_name': alch.VARCHAR(50),
                'driver_phone': alch.VARCHAR(20),
                'driver_SIM_type': alch.VARCHAR(5),
                'driver_SIM_num': alch.VARCHAR(20),
                'driver_date_cr': alch.DATETIME(),
                'driver_date_up': alch.DATETIME(),
                'driver_by_cr': alch.VARCHAR(50),
                'driver_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrdrivers ADD PRIMARY KEY (driver_id);')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_phone varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_type varchar(5) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_num varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_up varchar(50) NOT NULL;')

        addLog('Drivers','Add')
        return True, False, False, False, False, ''


#--------EDIT-------
@app.callback(
    Output('edit-notif-drivers','is_open'),
    [Input('confirm-edit-drivers','submit_n_clicks')],
    [State('data-table-edit-drivers','data')]
)
def editDriver(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)
    
    df_table.loc[(df_original_renamed["Nama Driver"] != df_table["Nama Driver"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nomor HP"] != df_table["Nomor HP"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tipe SIM"] != df_table["Tipe SIM"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nomor SIM"] != df_table["Nomor SIM"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Nama Driver"] != df_table["Nama Driver"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nomor HP"] != df_table["Nomor HP"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tipe SIM"] != df_table["Tipe SIM"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nomor SIM"] != df_table["Nomor SIM"]),"Diperbarui oleh"]= login_name
    
    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrdrivers'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'driver_id': alch.CHAR(36),
            'driver_name': alch.VARCHAR(50),
            'driver_phone': alch.VARCHAR(20),
            'driver_SIM_type': alch.VARCHAR(5),
            'driver_SIM_num': alch.VARCHAR(20),
            'driver_date_cr': alch.DATETIME(),
            'driver_date_up': alch.DATETIME(),
            'driver_by_cr': alch.VARCHAR(50),
            'driver_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrdrivers ADD PRIMARY KEY (driver_id);')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_phone varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_type varchar(5) NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_SIM_num varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrdrivers MODIFY driver_by_up varchar(50) NOT NULL;')

    addLog('Drivers','Edit')
    return True

@app.callback(
    Output('table-container-edit-drivers','children'),
    [Input('refresh-button-edit-drivers','n_clicks')]
)
def refEditDriver(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-drivers',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Driver', 'id':'Nama Driver', 'editable': True},
                {'name':'Nomor HP', 'id':'Nomor HP', 'editable': True},
                {'name':'Tipe SIM', 'id':'Tipe SIM', 'editable': True},
                {'name':'Nomor SIM', 'id':'Nomor SIM', 'editable': True},
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
    Output('table-refresh-drivers','children'),
    [Input('refresh-page-button-drivers','n_clicks')]
)
def refDriver(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-drivers',
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
    Output('table-container-drivers','children'),
    [Input('view-page-button-drivers','n_clicks')],
    [State('data-table-drivers','selected_rows'),State('data-table-drivers','data')]
)
def viewDriver(n, row_number, dataset):
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
    viewPhone = desire_data_df.iloc[0][2]
    viewSIMtype = desire_data_df.iloc[0][3]
    viewSIMnum = desire_data_df.iloc[0][4]
    viewDateCr = desire_data_df.iloc[0][5]
    viewDateUp = desire_data_df.iloc[0][6]
    viewByCr = desire_data_df.iloc[0][7]
    viewByUp = desire_data_df.iloc[0][8]

    return [
        html.H1('Lihat Driver', id='driver-header'),
        html.Div(id='button-container-view-drivers',children=[
            html.A(html.Button('Kembali', id='back-view-button-drivers'),href='/drivers')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-drivers'), html.Br(),
                    dbc.Label(viewID,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewName,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Nomor HP :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewPhone,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Tipe SIM :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewSIMtype,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Nomor SIM :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewSIMnum,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-drivers'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-drivers'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-drivers'),
                    html.Hr(),
                ])
            , id='row-view-drivers')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_drivers/")
def exportExcelDriver():
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
                     attachment_filename='drivers.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
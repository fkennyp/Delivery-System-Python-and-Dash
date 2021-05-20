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
SELECT vehicle_id, vehicle_name, vehicle_type 
FROM mstrgroupvehicles;
'''
query2 = '''
SELECT *
FROM mstrgroupvehicles;
'''
query_trans = '''
SELECT trans_vehicle
FROM transactiondelivery
'''
notAllColumns = {'vehicle_id':'ID', 'vehicle_name':'Nama Kendaraan', 'vehicle_type':'Tipe Kendaraan'}

AllColumns = {'vehicle_id':'ID',
              'vehicle_name':'Nama Kendaraan',
              'vehicle_type':'Tipe Kendaraan',
              'vehicle_date_cr':'Tanggal dibuat',
              'vehicle_date_up':'Tanggal diperbarui',
              'vehicle_by_cr':'Dibuat oleh',
              'vehicle_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'vehicle_id',
                 'Nama Kendaraan':'vehicle_name',
                 'Tipe Kendaraan':'vehicle_type',
                 'Tanggal dibuat':'vehicle_date_cr',
                 'Tanggal diperbarui':'vehicle_date_up',
                 'Dibuat oleh':'vehicle_by_cr',
                 'Diperbarui oleh':'vehicle_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'vehicle_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
vehicle_layout = html.Div([
    dcc.Location(id='vehicles-url',pathname='/vehicles'),
    navbar(),
    html.Div(id='table-container-vehicles', children=[
        html.H1('Kendaraan', id='vehicle-header'),
        html.Div(id='button-container-vehicles',children=[
            html.Button('Lihat',id='view-page-button-vehicles',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-vehicles',href='/vehicles/add'),id='add-page-button-vehicles'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-vehicles',href='/vehicles/edit'),id='edit-page-button-vehicles'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-vehicles',href='/vehicles/delete'),id='delete-page-button-vehicles'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-vehicles',href=''),id='refresh-page-button-vehicles'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-vehicles'),href='/download_excel_vehicles/'),
        ]),
        html.Div(id='table-refresh-vehicles',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-vehicles',
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
    dcc.Location(id='vehicles-add-url',pathname='/vehicles/add'),
    navbar(),
    html.H1('Tambah Kendaraan', id='vehicle-header'),
    html.Div(id='button-container-add-vehicles', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-vehicles'),
            id='confirm-add-vehicles',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-vehicles'),href='/vehicles')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-vehicles', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='vehicles-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='vehicles-add-label'),
                    dbc.Input(placeholder='Masukkan nama kendaraan...', id='vehicles-name-value'),
                    html.Br(),
                    dbc.Label('Tipe', className='vehicles-add-label'),
                    dbc.Input(placeholder='Masukkan tipe kendaraan...', id='vehicles-type-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='vehicles-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='vehicles-edit-url',pathname='/vehicles/edit'),
    navbar(),
    html.H1('Rubah Kendaraan', id='vehicle-header'),
    html.Div(id='button-container-edit-vehicles',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-vehicles'),
            id='confirm-edit-vehicles',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-vehicles',n_clicks=0),href='/vehicles'),
        html.Button(id='refresh-button-edit-vehicles',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-vehicles', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-vehicles',children=[
            dt.DataTable(
                id='data-table-edit-vehicles',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Kendaraan', 'id':'Nama Kendaraan', 'editable': True},
                    {'name':'Tipe Kendaraan', 'id':'Tipe Kendaraan', 'editable': True},
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
    dcc.Location(id='vehicles-del-url',pathname='/vehicles/delete'),
    navbar(),
    html.H1('Hapus Kendaraan', id='vehicle-header'),
    html.Div(id='button-container-del-vehicles',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-vehicles'),
            id='confirm-del-vehicles',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-vehicles',n_clicks=0),href='/vehicles'),
        html.Button(id='refresh-button-del-vehicles',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert(id='del-notif-vehicles', is_open=False, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-vehicles', children=[
            dt.DataTable(
                id='data-table-del-vehicles',
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

#----DELETE----
@app.callback(
    [Output('del-notif-vehicles','is_open'), Output('del-notif-vehicles','children'), Output('del-notif-vehicles','color'), Output('del-button-vehicles','disabled')],
    [Input('confirm-del-vehicles','submit_n_clicks')],
    [State('data-table-del-vehicles','data')]
)
def delVehicles(n, dataset):
    if not n:
        return False
    df_trans = pd.read_sql(query_trans,engine)
    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)

    df_trans2 = df_trans.drop_duplicates(subset=['trans_vehicle'])
    df_checker = df_trans2.assign(result=df_trans2['trans_vehicle'].isin(deleted_df_rev['vehicle_name']).astype(int))

    if 0 in df_checker.values: 
        return True,'Anda tidak bisa menghapus kendaraan yang masih berada di transaction!\nSilahkan refresh kembali page ini.','danger', 'True'
    else:
        tab_name = 'mstrgroupvehicles'
        deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'vehicle_id': alch.CHAR(36),
                'vehicle_name': alch.VARCHAR(50),
                'vehicle_type': alch.VARCHAR(50),
                'vehicle_date_cr': alch.DATETIME(),
                'vehicle_date_up': alch.DATETIME(),
                'vehicle_by_cr': alch.VARCHAR(50),
                'vehicle_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrgroupvehicles ADD PRIMARY KEY (vehicle_id);')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_type varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_up varchar(50) NOT NULL;')

        addLog('Vehicles','Delete')
        return True, 'Data berhasil dihapus', 'success', no_update

@app.callback(
    Output('table-container-del-vehicles','children'),
    [Input('refresh-button-del-vehicles','n_clicks')]
)
def refDelVehicles(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-vehicles',
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

#-------ADD------
@app.callback(
    [Output('add-notif-vehicles','is_open')]+\
        [Output('vehicles-'+x+'-value','invalid') for x in ['name','type']]+\
            [Output('vehicles-notice','children')],
    [Input('confirm-add-vehicles','submit_n_clicks')],
    [State('vehicles-'+x+'-value','value') for x in ['name','type']]
)
def addVehicles(n, vehiName, vehiType):
    if not n:
        return False, False, False, ''

    if not vehiName:
        return False, True, False, 'Nama kendaraan belum diisi!'
    elif not vehiType:
        return False, False, True, 'Tipe kendaraan belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['vehicle_id'] = str(uuid.uuid4())
        add_df_final['vehicle_name'] = vehiName
        add_df_final['vehicle_type'] = vehiType
        add_df_final['vehicle_date_cr'] = datetime.now()
        add_df_final['vehicle_date_up'] = datetime.now()
        add_df_final['vehicle_by_cr'] = login_name
        add_df_final['vehicle_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrgroupvehicles'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'vehicle_id': alch.CHAR(36),
                'vehicle_name': alch.VARCHAR(50),
                'vehicle_type': alch.VARCHAR(50),
                'vehicle_date_cr': alch.DATETIME(),
                'vehicle_date_up': alch.DATETIME(),
                'vehicle_by_cr': alch.VARCHAR(50),
                'vehicle_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrgroupvehicles ADD PRIMARY KEY (vehicle_id);')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_type varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_up varchar(50) NOT NULL;')

        addLog('Vehicles', 'Add')
        return True, False, False, ''

#-------EDIT------
@app.callback(
    Output('edit-notif-vehicles','is_open'),
    [Input('confirm-edit-vehicles','submit_n_clicks')],
    [State('data-table-edit-vehicles','data')]
)
def editVehicles(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama Kendaraan"] != df_table["Nama Kendaraan"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Tipe Kendaraan"] != df_table["Tipe Kendaraan"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Nama Kendaraan"] != df_table["Nama Kendaraan"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Tipe Kendaraan"] != df_table["Tipe Kendaraan"]),"Diperbarui oleh"]= login_name

    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrgroupvehicles'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'vehicle_id': alch.CHAR(36),
            'vehicle_name': alch.VARCHAR(50),
            'vehicle_type': alch.VARCHAR(50),
            'vehicle_date_cr': alch.DATETIME(),
            'vehicle_date_up': alch.DATETIME(),
            'vehicle_by_cr': alch.VARCHAR(50),
            'vehicle_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrgroupvehicles ADD PRIMARY KEY (vehicle_id);')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_type varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupvehicles MODIFY vehicle_by_up varchar(50) NOT NULL;')

    addLog('Vehicles','Edit')
    return True

@app.callback(
    Output('table-container-edit-vehicles','children'),
    [Input('refresh-button-edit-vehicles','n_clicks')]
)
def refEditVehicles(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-vehicles',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Kendaraan', 'id':'Nama Kendaraan', 'editable': True},
                {'name':'Tipe Kendaraan', 'id':'Tipe Kendaraan', 'editable': True},
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
    Output('table-refresh-vehicles','children'),
    [Input('refresh-page-button-vehicles','n_clicks')]
)
def refVehicles(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-vehicles',
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
    Output('table-container-vehicles','children'),
    [Input('view-page-button-vehicles','n_clicks')],
    [State('data-table-vehicles','selected_rows'),State('data-table-vehicles','data')]
)
def viewVehicles(n, row_number, dataset):
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
    viewDateCr = desire_data_df.iloc[0][3]
    viewDateUp = desire_data_df.iloc[0][4]
    viewByCr = desire_data_df.iloc[0][5]
    viewByUp = desire_data_df.iloc[0][6]

    return [
        html.H1('Lihat Kendaraan', id='vehicle-header'),
        html.Div(id='button-container-view-vehicles',children=[
            html.A(html.Button('Kembali', id='back-view-button-vehicles'),href='/vehicles')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-vehicles'), html.Br(),
                    dbc.Label(viewID,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewName,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Deskripsi :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewType,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-vehicles'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-vehicles'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-vehicles'),
                    html.Hr(),
                ])
            , id='row-view-vehicles')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_vehicles/")
def exportExcelVehicles():
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
                     attachment_filename='vehicles.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
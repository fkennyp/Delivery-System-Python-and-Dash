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
SELECT status_id, status_name, status_description 
FROM mstrstatus;
'''
query2 = '''
SELECT *
FROM mstrstatus;
'''
query_trans = '''
SELECT trans_status
FROM transactiondelivery
'''
notAllColumns = {'status_id':'ID', 'status_name':'Nama Status', 'status_description':'Deskripsi'}

AllColumns = {'status_id':'ID',
              'status_name':'Nama Status',
              'status_description':'Deskripsi',
              'status_date_cr':'Tanggal dibuat',
              'status_date_up':'Tanggal diperbarui',
              'status_by_cr':'Dibuat oleh',
              'status_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'status_id',
                 'Nama Status':'status_name',
                 'Deskripsi':'status_description',
                 'Tanggal dibuat':'status_date_cr',
                 'Tanggal diperbarui':'status_date_up',
                 'Dibuat oleh':'status_by_cr',
                 'Diperbarui oleh':'status_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'status_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
status_layout = html.Div([
    dcc.Location(id='status-url',pathname='/status'),
    navbar(),
    html.Div(id='table-container-status', children=[
        html.H1('Status', id='status-header'),
        html.Div(id='button-container-status',children=[
            html.Button('Lihat',id='view-page-button-status',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-status',href='/status/add'),id='add-page-button-status'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-status',href='/status/edit'),id='edit-page-button-status'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-status',href='/status/delete'),id='delete-page-button-status'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-status',href=''),id='refresh-page-button-status'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-status'),href='/download_excel_status/'),
        ]),
        html.Div(id='table-refresh-status',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-status',
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
    dcc.Location(id='status-add-url',pathname='/status/add'),
    navbar(),
    html.H1('Tambah Status', id='status-header'),
    html.Div(id='button-container-add-status', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-status'),
            id='confirm-add-status',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-status'),href='/status')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-status', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='status-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='status-add-label'),
                    dbc.Input(placeholder='Masukkan nama status...', id='status-name-value'),
                    html.Br(),
                    dbc.Label('Deskripsi', className='status-add-label'),
                    dbc.Input(placeholder='Masukkan deskripsi status...', id='status-description-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='status-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='status-edit-url',pathname='/status/edit'),
    navbar(),
    html.H1('Rubah Status', id='status-header'),
    html.Div(id='button-container-edit-status',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-status'),
            id='confirm-edit-status',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-status',n_clicks=0),href='/status'),
        html.Button(id='refresh-button-edit-status',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-status', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-status',children=[
            dt.DataTable(
                id='data-table-edit-status',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Status', 'id':'Nama Status', 'editable': True},
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
    dcc.Location(id='status-del-url',pathname='/status/delete'),
    navbar(),
    html.H1('Hapus Status', id='status-header'),
    html.Div(id='button-container-del-status',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-status'),
            id='confirm-del-status',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali',id='back-del-button-status',n_clicks=0),href='/status'),
        html.Button(id='refresh-button-del-status',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert(id='del-notif-status', is_open=False, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-status', children=[
            dt.DataTable(
                id='data-table-del-status',
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
    [Output('del-notif-status','is_open'), Output('del-notif-status','children'), Output('del-notif-status','color'), Output('del-button-status','disabled')],
    [Input('confirm-del-status','submit_n_clicks')],
    [State('data-table-del-status','data')]
)
def delStatus(n, dataset):
    if not n:
        return False

    df_trans = pd.read_sql(query_trans, engine)
    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)

    df_trans2 = df_trans.drop_duplicates(subset=['trans_status'])
    df_checker = df_trans2.assign(result=df_trans2['trans_status'].isin(deleted_df_rev['status_name']).astype(int))

    if 0 in df_checker.values: 
        return True,'Anda tidak bisa menghapus status yang masih berada di transaction!\nSilahkan refresh kembali page ini.','danger', 'True'
    else:
        tab_name = 'mstrstatus'
        deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'status_id': alch.CHAR(36),
                'status_name': alch.VARCHAR(50),
                'status_description': alch.VARCHAR(300),
                'status_date_cr': alch.DATETIME(),
                'status_date_up': alch.DATETIME(),
                'status_by_cr': alch.VARCHAR(50),
                'status_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrstatus ADD PRIMARY KEY (status_id);')
            con.execute('ALTER TABLE mstrstatus MODIFY status_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_description varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_by_up varchar(50) NOT NULL;')

        addLog('Status','Delete')
        return True, 'Data berhasil dihapus', 'success', no_update

@app.callback(
    Output('table-container-del-status','children'),
    [Input('refresh-button-del-status','n_clicks')]
)
def refDelStatus(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-status',
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
    [Output('add-notif-status','is_open')]+\
        [Output('status-'+x+'-value','invalid') for x in ['name','description']]+\
            [Output('status-notice','children')],
    [Input('confirm-add-status','submit_n_clicks')],
    [State('status-'+x+'-value','value') for x in ['name','description']]
)
def addStatus(n, name, descrip):
    if not n:
        return False, False, False, ''

    if not name:
        return False, True, False, 'Nama status belum diisi!'
    elif not descrip:
        return False, False, True, 'Deskripsi status belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['status_id'] = str(uuid.uuid4())
        add_df_final['status_name'] = name
        add_df_final['status_description'] = descrip
        add_df_final['status_date_cr'] = datetime.now()
        add_df_final['status_date_up'] = datetime.now()
        add_df_final['status_by_cr'] = login_name
        add_df_final['status_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)
        
        tab_name = 'mstrstatus'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'status_id': alch.CHAR(36),
                'status_name': alch.VARCHAR(50),
                'status_description': alch.VARCHAR(300),
                'status_date_cr': alch.DATETIME(),
                'status_date_up': alch.DATETIME(),
                'status_by_cr': alch.VARCHAR(50),
                'status_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrstatus ADD PRIMARY KEY (status_id);')
            con.execute('ALTER TABLE mstrstatus MODIFY status_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_description varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrstatus MODIFY status_by_up varchar(50) NOT NULL;')

        addLog('Status', 'Add')
        return True, False, False, ''
    
#------EDIT-----

@app.callback(
    Output('edit-notif-status','is_open'),
    [Input('confirm-edit-status','submit_n_clicks')],
    [State('data-table-edit-status','data')]
)
def editStatus(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama Status"] != df_table["Nama Status"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Nama Status"] != df_table["Nama Status"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Diperbarui oleh"]= login_name
    
    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrstatus'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'status_id': alch.CHAR(36),
            'status_name': alch.VARCHAR(50),
            'status_description': alch.VARCHAR(300),
            'status_date_cr': alch.DATETIME(),
            'status_date_up': alch.DATETIME(),
            'status_by_cr': alch.VARCHAR(50),
            'status_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrstatus ADD PRIMARY KEY (status_id);')
        con.execute('ALTER TABLE mstrstatus MODIFY status_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrstatus MODIFY status_description varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrstatus MODIFY status_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrstatus MODIFY status_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrstatus MODIFY status_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrstatus MODIFY status_by_up varchar(50) NOT NULL;')

    addLog('Status','Edit')
    return True

@app.callback(
    Output('table-container-edit-status','children'),
    [Input('refresh-button-edit-status','n_clicks')]
)
def refEditStatus(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-status',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Status', 'id':'Nama Status', 'editable': True},
                {'name':'Deskripsi', 'id':'Deskripsi', 'editable': True},
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
    Output('table-refresh-status','children'),
    [Input('refresh-page-button-status','n_clicks')]
)
def refStatus(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-status',
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
    Output('table-container-status','children'),
    [Input('view-page-button-status','n_clicks')],
    [State('data-table-status','selected_rows'),State('data-table-status','data')]
)
def viewStatus(n, row_number, dataset):
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
    viewDesc = desire_data_df.iloc[0][2]
    viewDateCr = desire_data_df.iloc[0][3]
    viewDateUp = desire_data_df.iloc[0][4]
    viewByCr = desire_data_df.iloc[0][5]
    viewByUp = desire_data_df.iloc[0][6]

    return [
        html.H1('Lihat Status', id='status-header'),
        html.Div(id='button-container-view-status',children=[
            html.A(html.Button('Kembali', id='back-view-button-status'),href='/status')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-status'), html.Br(),
                    dbc.Label(viewID,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-status'),html.Br(),
                    dbc.Label(viewName,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Deskripsi :', className='view-value-status'),html.Br(),
                    dbc.Label(viewDesc,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-status'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-status'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-status'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-status'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-status'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-status'),
                    html.Hr(),
                ])
            , id='row-view-status')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_status/")
def exportExcelStatus():
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
                     attachment_filename='status.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
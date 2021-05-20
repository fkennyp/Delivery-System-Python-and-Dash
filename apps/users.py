import dash
import dash_table as dt
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
import sqlalchemy as alch
import io, flask, base64, hashlib
from dash.dependencies import Input, Output, State
from datetime import datetime
from flask import send_file
from dash import no_update

from app import app
from apps import login
from modules import navbar, styleCell, styleHeader, styleTable, addLog

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT user_id, user_name, user_phone, user_email, user_address, user_role, user_location
FROM mstrusers;
'''
query2 = '''
SELECT *
FROM mstrusers;
'''
query_stores = '''
SELECT store_name
FROM mstrstores;
'''
df_stores = pd.read_sql(query_stores, engine)
stores = [{'label':x, 'value':x} for x in df_stores['store_name'].unique()]

notAllColumns = {'user_id':'ID', 
                 'user_name':'Nama User', 
                 'user_phone':'Nomor HP',
                 'user_email':'Email',
                 'user_address':'Alamat',
                 'user_location':'Lokasi',
                 'user_role':'Role'}

AllColumns = {'user_id':'ID',
              'user_login':'Login',
              'user_name':'Nama User',
              'user_password':'Password',
              'user_phone':'Nomor HP',
              'user_email':'Email',
              'user_address':'Alamat',
              'user_role':'Role',
              'user_location':'Lokasi',
              'user_date_cr':'Tanggal dibuat',
              'user_date_up':'Tanggal diperbarui',
              'user_by_cr':'Dibuat oleh',
              'user_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'user_id',
                 'Login':'user_login',
                 'Nama User':'user_name',
                 'Password':'user_password',
                 'Nomor HP':'user_phone',
                 'Email':'user_email',
                 'Alamat':'user_address',
                 'Role':'user_role',
                 'Lokasi':'user_location',
                 'Tanggal dibuat':'user_date_cr',
                 'Tanggal diperbarui':'user_date_up',
                 'Dibuat oleh':'user_by_cr',
                 'Diperbarui oleh':'user_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'user_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
users_layout = html.Div([
    dcc.Location(id='users-url',pathname='/users'),
    navbar(),
    html.Div(id='table-container-users', children=[
        html.H1('User', id='user-header'),
        html.Div(id='button-container-users',children=[
            html.Button('Lihat',id='view-page-button-users',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-users',href='/users/add'),id='add-page-button-users'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-users',href='/users/edit'),id='edit-page-button-users'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-users',href='/users/delete'),id='delete-page-button-users'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-users',href=''),id='refresh-page-button-users'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-users'),href='/download_excel_users/'),
        ]),
        html.Div(id='table-refresh-users',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-users',
                columns=[{'name':i,'id':i} for i in df_renamed.columns],
                data=df_renamed.to_dict('records'),                    
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
        ])
    ])
])

add_layout = html.Div([
    dcc.Location(id='users-add-url',pathname='/users/add'),
    navbar(),
    html.H1('Tambah User', id='user-header'),
    html.Div(id='button-container-add-users', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-users'),
            id='confirm-add-users',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-users'),href='/users')
    ]),
    dbc.Spinner(children=[

        dbc.Alert('Data berhasil ditambahkan',id='add-notif-users', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='users-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Login', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan login...', id='users-login-value'),
                    html.Br(),
                    dbc.Label('Nama User', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan nama user...', id='users-name-value'),
                    html.Br(),
                    dbc.Label('Password', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan password...', type='password', id='users-password-value'),
                    html.Br(),
                    dbc.Label('Nomor HP', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan nomor HP...', id='users-phone-value'),
                    html.Br(),
                    dbc.Label('Email', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan email...', id='users-email-value'),
                    html.Br(),
                    dbc.Label('Alamat', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan alamat...', id='users-address-value'),
                    html.Br(),
                    dbc.Label('Role', className='users-add-label'),
                    dbc.Input(placeholder='Masukkan role...', id='users-role-value'),
                    html.Br(),
                    dbc.Label('Lokasi', className='users-add-label'),
                    dcc.Dropdown(
                        id='users-location-value',
                        options = stores,
                        searchable=True,
                        placeholder='Pilih lokasi...',
                        clearable=True
                    ),
                    html.Hr()
                ])
            ])
        , id='users-row'),
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='users-edit-url',pathname='/users/edit'),
    navbar(),
    html.H1('Rubah User', id='user-header'),
    html.Div(id='button-container-edit-users',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-users'),
            id='confirm-edit-users',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali', id='back-edit-button-users',n_clicks=0),href='/users'),
        html.Button(id='refresh-button-edit-users',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-users', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-edit-users',children=[
            dt.DataTable(
                id='data-table-edit-users',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Login', 'id':'Login', 'editable': False},
                    {'name':'Nama User', 'id':'Nama User', 'editable': True},
                    {'name':'Password', 'id':'Password', 'editable': False},
                    {'name':'Nomor HP', 'id':'Nomor HP', 'editable': True},
                    {'name':'Email', 'id':'Email', 'editable': True},
                    {'name':'Alamat', 'id':'Alamat', 'editable': True},
                    {'name':'Role', 'id':'Role', 'editable': False},
                    {'name':'Lokasi', 'id':'Lokasi', 'editable': True},
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
    dcc.Location(id='users-del-url',pathname='/users/delete'),
    navbar(),
    html.H1('Hapus User', id='user-header'),
    html.Div(id='button-container-del-users',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-users'),
            id='confirm-del-users',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-users',n_clicks=0),href='/users'),
        html.Button(id='refresh-button-del-users',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil dihapus',id='del-notif-users', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-users', children=[
            dt.DataTable(
                id='data-table-del-users',
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

#-------DELETE------
@app.callback(
    Output('del-notif-users','is_open'),
    [Input('confirm-del-users','submit_n_clicks')],
    [State('data-table-del-users','data')]
)
def DelUsers(n, dataset):
    if not n:
        return False

    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    tab_name = 'mstrusers'
    deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'user_id': alch.CHAR(36),
            'user_login': alch.VARCHAR(50),
            'user_name': alch.VARCHAR(50),
            'user_password': alch.VARCHAR(50),
            'user_phone': alch.VARCHAR(20),
            'user_email': alch.VARCHAR(50),
            'user_address': alch.VARCHAR(300),
            'user_role': alch.VARCHAR(20),
            'user_location': alch.VARCHAR(100),
            'user_date_cr': alch.DATETIME(),
            'user_date_up': alch.DATETIME(),
            'user_by_cr': alch.VARCHAR(50),
            'user_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrusers ADD PRIMARY KEY (user_id);')
        con.execute('ALTER TABLE mstrusers MODIFY user_login varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_password varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_phone varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_email varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_address varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_role varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_location varchar(100) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_by_up varchar(50) NOT NULL;')
    
    addLog('Users','Delete')
    return True

@app.callback(
    Output('table-container-del-users','children'),
    [Input('refresh-button-del-users','n_clicks')]
)
def refDelUsers(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-users',
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
    [Output('add-notif-users','is_open')]+\
        [Output('users-'+x+'-value','invalid') for x in ['login','name','password','phone','email','address','role','location']]+\
            [Output('users-notice','children')],
    [Input('confirm-add-users','submit_n_clicks')],
    [State('users-'+x+'-value','value') for x in ['login','name','password','phone','email','address','role','location']]
)
def addUsers(n, userlog, username, userpass, userphone, useremail, useraddress, userrole, userlocation):
    if not n:
        return False, False, False, False, False, False, False, False, False, ''

    if not userlog:
        return False, True, False, False, False, False, False, False, False, 'Login user belum diisi!'
    elif not username:
        return False, False, True, False, False, False, False, False, False, 'Nama user belum diisi!'
    elif not userpass:
        return False, False, False, True, False, False, False, False, False, 'Password user belum diisi!'
    elif not userphone:
        return False, False, False, False, True, False, False, False, False, 'Nomor HP user belum diisi!'
    elif not useremail:
        return False, False, False, False, False, True, False, False, False, 'Email user belum diisi!'
    elif not useraddress:
        return False, False, False, False, False, False, True, False, False, 'Alamat user belum diisi!'
    elif not userrole:
        return False, False, False, False, False, False, False, True, False, 'Role user belum diisi!'
    elif not userlocation:
        return False, False, False, False, False, False, False, False, True, 'Lokasi user belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['user_id'] = str(uuid.uuid4())
        add_df_final['user_login'] = userlog
        add_df_final['user_name'] = username
        add_df_final['user_password'] = base64.b64encode(hashlib.sha1(userpass.encode('UTF-8')).digest())
        add_df_final['user_phone'] = userphone
        add_df_final['user_email'] = useremail
        add_df_final['user_address'] = useraddress
        add_df_final['user_role'] = userrole
        add_df_final['user_location'] = userlocation
        add_df_final['user_date_cr'] = datetime.now()
        add_df_final['user_date_up'] = datetime.now()
        add_df_final['user_by_cr'] = login_name
        add_df_final['user_by_up'] = login_name
        
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrusers'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'user_id': alch.CHAR(36),
                'user_login': alch.VARCHAR(50),
                'user_name': alch.VARCHAR(50),
                'user_password': alch.VARCHAR(50),
                'user_phone': alch.VARCHAR(20),
                'user_email': alch.VARCHAR(50),
                'user_address': alch.VARCHAR(300),
                'user_role': alch.VARCHAR(20),
                'user_location': alch.VARCHAR(100),
                'user_date_cr': alch.DATETIME(),
                'user_date_up': alch.DATETIME(),
                'user_by_cr': alch.VARCHAR(50),
                'user_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrusers ADD PRIMARY KEY (user_id);')
            con.execute('ALTER TABLE mstrusers MODIFY user_login varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_password varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_phone varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_email varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_address varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_role varchar(20) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_location varchar(100) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrusers MODIFY user_by_up varchar(50) NOT NULL;')

        addLog('Users', 'Add')
        return True, False, False, False, False, False, False, False, False, ''

#------EDIT-----

@app.callback(
    Output('edit-notif-users','is_open'),
    [Input('confirm-edit-users','submit_n_clicks')],
    [State('data-table-edit-users','data')]
)
def editUsers(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama User"] != df_table["Nama User"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Nomor HP"] != df_table["Nomor HP"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Email"] != df_table["Email"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Alamat"] != df_table["Alamat"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Role"] != df_table["Role"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Lokasi"] != df_table["Lokasi"]),"Tanggal diperbarui"]=datetime.now()
    
    df_table.loc[(df_original_renamed["Nama User"] != df_table["Nama User"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Nomor HP"] != df_table["Nomor HP"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Email"] != df_table["Email"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Alamat"] != df_table["Alamat"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Role"] != df_table["Role"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Lokasi"] != df_table["Lokasi"]),"Diperbarui oleh"]= login_name

    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrusers'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'user_id': alch.CHAR(36),
            'user_login': alch.VARCHAR(50),
            'user_name': alch.VARCHAR(50),
            'user_password': alch.VARCHAR(50),
            'user_phone': alch.VARCHAR(20),
            'user_email': alch.VARCHAR(50),
            'user_address': alch.VARCHAR(300),
            'user_role': alch.VARCHAR(20),
            'user_location': alch.VARCHAR(100),
            'user_date_cr': alch.DATETIME(),
            'user_date_up': alch.DATETIME(),
            'user_by_cr': alch.VARCHAR(50),
            'user_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrusers ADD PRIMARY KEY (user_id);')
        con.execute('ALTER TABLE mstrusers MODIFY user_login varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_password varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_phone varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_email varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_address varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_role varchar(20) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_location varchar(100) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrusers MODIFY user_by_up varchar(50) NOT NULL;')

    addLog('Users','Edit')
    return True

@app.callback(
    Output('table-container-edit-users','children'),
    [Input('refresh-button-edit-users','n_clicks')]
)
def refEditUsers(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-users',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Login', 'id':'Login', 'editable': False},
                {'name':'Nama User', 'id':'Nama User', 'editable': True},
                {'name':'Password', 'id':'Password', 'editable': False},
                {'name':'Nomor HP', 'id':'Nomor HP', 'editable': True},
                {'name':'Email', 'id':'Email', 'editable': True},
                {'name':'Alamat', 'id':'Alamat', 'editable': True},
                {'name':'Role', 'id':'Role', 'editable': False},
                {'name':'Lokasi', 'id':'Lokasi', 'editable': True},
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
    Output('table-refresh-users','children'),
    [Input('refresh-page-button-users','n_clicks')]
)
def refUsers(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-users',
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
    Output('table-container-users','children'),
    [Input('view-page-button-users','n_clicks')],
    [State('data-table-users','selected_rows'),State('data-table-users','data')]
)
def viewUsers(n, row_number, dataset):
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
    viewLogin = desire_data_df.iloc[0][1]
    viewName = desire_data_df.iloc[0][2]
    viewPass = desire_data_df.iloc[0][3]
    viewPhone = desire_data_df.iloc[0][4]
    viewEmail = desire_data_df.iloc[0][5]
    viewAddress = desire_data_df.iloc[0][6]
    viewRole = desire_data_df.iloc[0][7]
    viewLocation = desire_data_df.iloc[0][8]
    viewDateCr = desire_data_df.iloc[0][9]
    viewDateUp = desire_data_df.iloc[0][10]
    viewByCr = desire_data_df.iloc[0][11]
    viewByUp = desire_data_df.iloc[0][12]

    return [
        html.H1('Lihat User', id='user-header'),
        html.Div(id='button-container-view-users',children=[
            html.A(html.Button('Kembali', id='back-view-button-users'),href='/users')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-users'), html.Br(),
                    dbc.Label(viewID,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Login :', className='view-value-users'),html.Br(),
                    dbc.Label(viewLogin,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-users'),html.Br(),
                    dbc.Label(viewName,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Password :', className='view-value-users'),html.Br(),
                    dbc.Label(viewPass,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Nomor HP :', className='view-value-users'),html.Br(),
                    dbc.Label(viewPhone,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Email :', className='view-value-users'),html.Br(),
                    dbc.Label(viewEmail,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Alamat :', className='view-value-users'),html.Br(),
                    dbc.Label(viewAddress,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Role :', className='view-value-users'),html.Br(),
                    dbc.Label(viewRole,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Lokasi :', className='view-value-users'),html.Br(),
                    dbc.Label(viewLocation,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-users'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-users'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-users'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-users'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-users'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-users'),
                    html.Hr(),
                ])
            , id='row-view-users')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_users/")
def exportExcelUsers():
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
                     attachment_filename='users.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
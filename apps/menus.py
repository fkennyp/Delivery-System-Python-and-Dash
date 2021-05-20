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
SELECT menu_id, menu_name, menu_description 
FROM mstrmenus;
'''
query2 = '''
SELECT *
FROM mstrmenus;
'''
notAllColumns = {'menu_id':'ID', 'menu_name':'Nama Menu', 'menu_description':'Deskripsi'}

AllColumns = {'menu_id':'ID',
              'menu_name':'Nama Menu',
              'menu_description':'Deskripsi',
              'menu_date_cr':'Tanggal dibuat',
              'menu_date_up':'Tanggal diperbarui',
              'menu_by_cr':'Dibuat oleh',
              'menu_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'menu_id',
                 'Nama Menu':'menu_name',
                 'Deskripsi':'menu_description',
                 'Tanggal dibuat':'menu_date_cr',
                 'Tanggal diperbarui':'menu_date_up',
                 'Dibuat oleh':'menu_by_cr',
                 'Diperbarui oleh':'menu_by_up'}

df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
                                  
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns )
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'menu_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
menu_layout = html.Div([
    dcc.Location(id='menus-url',pathname='/menus'),
    navbar(),
    html.Div(id='table-container-menus', children=[
        html.H1('Menu', id='menu-header'),
        html.Div(id='button-container-menus',children=[
            html.Button('Lihat',id='view-page-button-menus',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-menus',href='/menus/add'),id='add-page-button-menus'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-menus',href='/menus/edit'),id='edit-page-button-menus'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-menus',href='/menus/delete'),id='delete-page-button-menus'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-menus',href=''),id='refresh-page-button-menus'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-menus'),href='/download_excel_menus/'),
        ]),
        html.Div(id='table-refresh-menus',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-menus',
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
    dcc.Location(id='menus-add-url',pathname='/menus/add'),
    navbar(),
    html.H1('Tambah Menu', id='menu-header'),
    
    html.Div(id='button-container-add-menus', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='add-button-menus'),
            id='confirm-add-menus',
            message='Anda yakin ingin menambahkan data?',
        ),
        html.A(html.Button('Kembali', id='back-add-button-menus'),href='/menus')
    ]),    
        
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-menus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='menus-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='menus-add-label'),
                    dbc.Input(placeholder='Masukkan nama menu...', id='menus-name-value'),
                    html.Br(),
                    dbc.Label('Deskripsi', className='menus-add-label'),
                    dbc.Input(placeholder='Masukkan deskripsi...', id='menus-description-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='menus-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='menus-edit-url',pathname='/menus/edit'),
    navbar(),
    html.H1('Rubah Menu', id='menu-header'),
    
    html.Div(id='button-container-edit-menus',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-menus'),
            id='confirm-edit-menus',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-menus',n_clicks=0),href='/menus'),
        html.Button(id='refresh-button-edit-menus',n_clicks=0)
    ]),
    
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-menus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        html.Div(id='table-container-edit-menus',children=[
            dt.DataTable(
                id='data-table-edit-menus',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Menu', 'id':'Nama Menu', 'editable': True},
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
    dcc.Location(id='menus-del-url',pathname='/menus/delete'),
    navbar(),
    html.H1('Hapus Menu', id='menu-header'),
    html.Div(id='button-container-del-menus',children=[
        dcc.ConfirmDialogProvider(children= 
            html.Button('Kirim', id='del-button-menus'),
            id='confirm-del-menus',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-menus',n_clicks=0),href='/menus'),
        html.Button(id='refresh-button-del-menus',n_clicks=0)
    ]),
        
    
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil dihapus',id='del-notif-menus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),

        html.Div(id='table-container-del-menus', children=[
            dt.DataTable(
                id='data-table-del-menus',
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
    Output('del-notif-menus','is_open'),
    [Input('confirm-del-menus','submit_n_clicks')],
    [State('data-table-del-menus','data')]
)
def delMenus(n, dataset):
    if not n:
        return False

    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    tab_name = 'mstrmenus'
    deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'menu_id': alch.CHAR(36),
            'menu_name': alch.VARCHAR(50),
            'menu_description': alch.VARCHAR(300),
            'menu_date_cr': alch.DATETIME(),
            'menu_date_up': alch.DATETIME(),
            'menu_by_cr': alch.VARCHAR(50),
            'menu_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrmenus ADD PRIMARY KEY (menu_id);')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_description varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_by_up varchar(50) NOT NULL;')
        
    addLog('Menus','Delete')
    return True

@app.callback(
    Output('table-container-del-menus','children'),
    [Input('refresh-button-del-menus','n_clicks')]
)
def refDelMenus(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-menus',
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
    [Output('add-notif-menus','is_open')]+\
        [Output('menus-'+x+'-value','invalid') for x in ['name','description']]+\
            [Output('menus-notice','children')],
    [Input('confirm-add-menus','submit_n_clicks')],
    [State('menus-'+x+'-value','value') for x in ['name','description']]
)
def addMenus(n, menuName, menuDescrip):
    if not n:
        return False, False, False, ''

    if not menuName:
        return False, True, False, 'Nama menu belum diisi!'
    elif not menuDescrip:
        return False, False, True, 'Deskripsi menu belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['menu_id'] = str(uuid.uuid4())
        add_df_final['menu_name'] = menuName
        add_df_final['menu_description'] = menuDescrip
        add_df_final['menu_date_cr'] = datetime.now()
        add_df_final['menu_date_up'] = datetime.now()
        add_df_final['menu_by_cr'] = login_name
        add_df_final['menu_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrmenus'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'menu_id': alch.CHAR(36),
                'menu_name': alch.VARCHAR(50),
                'menu_description': alch.VARCHAR(300),
                'menu_date_cr': alch.DateTime(),
                'menu_date_up': alch.DateTime(),
                'menu_by_cr': alch.VARCHAR(50),
                'menu_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrmenus ADD PRIMARY KEY (menu_id);')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_description varchar(300) NOT NULL;')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrmenus MODIFY menu_by_up varchar(50) NOT NULL;')

        addLog('Menus','Add')
        return True, False, False, ''

#----------EDIT---------

@app.callback(
    Output('edit-notif-menus','is_open'),
    [Input('confirm-edit-menus','submit_n_clicks')],
    [State('data-table-edit-menus','data')]
)
def editMenus(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset)
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama Menu"] != df_table["Nama Menu"]),"Tanggal diperbarui"]=datetime.now()
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Tanggal diperbarui"]=datetime.now()

    df_table.loc[(df_original_renamed["Nama Menu"] != df_table["Nama Menu"]),"Diperbarui oleh"]= login_name
    df_table.loc[(df_original_renamed["Deskripsi"] != df_table["Deskripsi"]),"Diperbarui oleh"]= login_name
    
    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrmenus'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'menu_id': alch.CHAR(36),
            'menu_name': alch.VARCHAR(50),
            'menu_description': alch.VARCHAR(300),
            'menu_date_cr': alch.DateTime(),
            'menu_date_up': alch.DateTime(),
            'menu_by_cr': alch.VARCHAR(50),
            'menu_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrmenus ADD PRIMARY KEY (menu_id);')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_description varchar(300) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrmenus MODIFY menu_by_up varchar(50) NOT NULL;')

    addLog('Menus','Edit')
    return True

@app.callback(
    Output('table-container-edit-menus','children'),
    [Input('refresh-button-edit-menus','n_clicks')]
)
def refEditMenus(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-menus',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Menu', 'id':'Nama Menu', 'editable': True},
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
    Output('table-refresh-menus','children'),
    [Input('refresh-page-button-menus','n_clicks')]
)
def refMenus(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-menus',
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
    Output('table-container-menus','children'),
    [Input('view-page-button-menus','n_clicks')],
    [State('data-table-menus','selected_rows'),State('data-table-menus','data')]
)
def viewMenus(n, row_number, dataset):
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
        html.H1('Lihat Menu', id='menu-header'),
        html.Div(id='button-container-view-menus',children=[
            html.A(html.Button('Kembali', id='back-view-button-menus'),href='/menus')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-menus'), html.Br(),
                    dbc.Label(viewID,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewName,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Deskripsi :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewDesc,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-menus'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-menus'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-menus'),
                    html.Hr(),
                ])
            , id='row-view-menus')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_menus/")
def exportExcelMenus():
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
                     attachment_filename='menus.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
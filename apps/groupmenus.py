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
SELECT group_menu_id, group_menu_name
FROM mstrgroupmenus;
'''
query2 = '''
SELECT *
FROM mstrgroupmenus;
'''
notAllColumns = {'group_menu_id':'ID', 'group_menu_name':'Nama Grup Menu'}

AllColumns = {'group_menu_id':'ID',
              'group_menu_name':'Nama Grup Menu',
              'group_menu_date_cr':'Tanggal dibuat',
              'group_menu_date_up':'Tanggal diperbarui',
              'group_menu_by_cr':'Dibuat oleh',
              'group_menu_by_up':'Diperbarui oleh'}

RevAllColumns = {'ID':'group_menu_id',
                 'Nama Grup Menu':'group_menu_name',
                 'Tanggal dibuat':'group_menu_date_cr',
                 'Tanggal diperbarui':'group_menu_date_up',
                 'Dibuat oleh':'group_menu_by_cr',
                 'Diperbarui oleh':'group_menu_by_up'}


df = pd.read_sql(query,engine)
df_renamed = df.rename(columns = notAllColumns)
df2 = pd.read_sql(query2,engine)
df2_renamed = df2.rename(columns = AllColumns)
#------------------TABLE STYLING--------------
styleCondition=[
    {'if': {'column_id': 'group_menu_id'},
    'width': '200px'},
]
#--------------LAYOUTS----------------------------
groupmenu_layout = html.Div([
    dcc.Location(id='groupmenu-url',pathname='/groupmenus'),
    navbar(),
    html.Div(id='table-container-groupmenus', children=[
        html.H1('Group Menu', id='groupmenu-header'),
        html.Div(id='button-container-groupmenus',children=[
            html.Button('Lihat',id='view-page-button-groupmenus',n_clicks=0),
            html.Button(dcc.Link('Tambah',id='add-page-link-groupmenus',href='/groupmenus/add'),id='add-page-button-groupmenus'),
            html.Button(dcc.Link('Rubah',id='edit-page-link-groupmenus',href='/groupmenus/edit'),id='edit-page-button-groupmenus'),
            html.Button(dcc.Link('Hapus',id='delete-page-link-groupmenus',href='/groupmenus/delete'),id='delete-page-button-groupmenus'),
            html.Button(dcc.Link('Refresh',id='refresh-page-link-groupmenus',href=''),id='refresh-page-button-groupmenus'), #utk ngerefresh
            html.A(html.Button('Export ke excel', id='export-groupmenus'),href='/download_excel_groupmenus/'),
        ]),
        html.Div(id='table-refresh-groupmenus',children=[ #ini perlu agar setelah update_db, data kerefresh
            dt.DataTable(
                id='data-table-groupmenus',
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
    dcc.Location(id='groupmenus-add-url',pathname='/groupmenus/add'),
    navbar(),
    html.H1('Tambah Group Menu', id='groupmenu-header'),
    html.Div(id='button-container-add-groupmenus', children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='add-button-groupmenus'),
            id='confirm-add-groupmenus',
            message='Anda yakin ingin menambahkan data?'
        ),
        html.A(html.Button('Kembali', id='back-add-button-groupmenus'),href='/groupmenus')
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil ditambahkan',id='add-notif-groupmenus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        dbc.Row(
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label(id='groupmenus-notice', style={'font-family':'sans-serif','fontWeight':'bold','fontSize':'16pt', 'color':'red'}),
                    html.Hr(),
                    dbc.Label('Nama', className='groupmenus-add-label'),
                    dbc.Input(placeholder='Masukkan nama grup menu...', id='groupmenus-name-value'),
                    html.Br(),
                    html.Hr()
                ])
            ])
        , id='groupmenus-row')
    ], size='lg', type='grow', fullscreen=True, color='danger')
])

edit_layout = html.Div([
    dcc.Location(id='groupmenus-edit-url',pathname='/groupmenus/edit'),
    navbar(),
    html.H1('Rubah Group Menu', id='groupmenu-header'),
    html.Div(id='button-container-edit-groupmenus',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim',id='edit-button-groupmenus'),
            id='confirm-edit-groupmenus',
            message='Anda yakin ingin merubah data?'
        ),
        html.A(html.Button('Kembali',id='back-edit-button-groupmenus',n_clicks=0),href='/groupmenus'),
        html.Button(id='refresh-button-edit-groupmenus',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil diubah',id='edit-notif-groupmenus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        html.Div(id='table-container-edit-groupmenus',children=[
            dt.DataTable(
                id='data-table-edit-groupmenus',
                columns=[
                    {'name':'ID', 'id':'ID', 'editable': False},
                    {'name':'Nama Grup Menu', 'id':'Nama Grup Menu', 'editable': True},
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
    dcc.Location(id='groupmenus-del-url',pathname='/groupmenus/delete'),
    navbar(),
    html.H1('Hapus Group Menu', id='groupmenu-header'),
    html.Div(id='button-container-del-groupmenus',children=[
        dcc.ConfirmDialogProvider(children=
            html.Button('Kirim', id='del-button-groupmenus'),
            id='confirm-del-groupmenus',
            message='Anda yakin ingin menghapus data?'
        ),
        html.A(html.Button('Kembali', id='back-del-button-groupmenus',n_clicks=0),href='/groupmenus'),
        html.Button(id='refresh-button-del-groupmenus',n_clicks=0)
    ]),
    dbc.Spinner(children=[
        dbc.Alert('Data berhasil dihapus',id='del-notif-groupmenus', is_open=True, dismissable=True, style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'}),
        html.Div(id='table-container-del-groupmenus', children=[
            dt.DataTable(
                id='data-table-del-groupmenus',
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

#------DELETE----
@app.callback(
    Output('del-notif-groupmenus','is_open'),
    [Input('confirm-del-groupmenus','submit_n_clicks')],
    [State('data-table-del-groupmenus','data')]
)
def delGroupMenus(n, dataset):
    if not n:
        return False

    login_name = login.logged_login
    deleted_df = pd.DataFrame(dataset)
    deleted_df_rev = deleted_df.rename(columns = RevAllColumns)
    tab_name = 'mstrgroupmenus'
    deleted_df_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'group_menu_id': alch.CHAR(36),
            'group_menu_name': alch.VARCHAR(50),
            'group_menu_date_cr': alch.DATETIME(),
            'group_menu_date_up': alch.DATETIME(),
            'group_menu_by_cr': alch.VARCHAR(50),
            'group_menu_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrgroupmenus ADD PRIMARY KEY (group_menu_id);')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_up varchar(50) NOT NULL;')

    addLog('Group Menus','Delete')
    return True

@app.callback(
    Output('table-container-del-groupmenus','children'),
    [Input('refresh-button-del-groupmenus','n_clicks')]
)
def refDelGroupMenus(n):
    df6 = pd.read_sql(query2,engine)
    df6_renamed = df6.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-del-groupmenus',
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

#-----ADD-----
@app.callback(
    [Output('add-notif-groupmenus','is_open')]+\
        [Output('groupmenus-'+x+'-value','invalid') for x in ['name']]+\
            [Output('groupmenus-notice','children')],
    [Input('confirm-add-groupmenus','submit_n_clicks')],
    [State('groupmenus-'+x+'-value','value') for x in ['name']]
)
def addGroupMenus(n, groupmenuName):
    if not n:
        return False, False, ''

    if not groupmenuName:
        return False, True, 'Nama grup menu belum diisi!'
    else:
        login_name = login.logged_login

        df_ori = pd.read_sql(query2, engine)
        add_df = [{x:''} for x in df_ori.columns]
        add_df_final = {}
        for cols in add_df:
            add_df_final.update(cols)

        add_df_final['group_menu_id'] = str(uuid.uuid4())
        add_df_final['group_menu_name'] = groupmenuName
        add_df_final['group_menu_date_cr'] = datetime.now()
        add_df_final['group_menu_date_up'] = datetime.now()
        add_df_final['group_menu_by_cr'] = login_name
        add_df_final['group_menu_by_up'] = login_name
    
        df_ori = df_ori.append(add_df_final, ignore_index=True)

        tab_name = 'mstrgroupmenus'
        df_ori.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
            dtype={
                'group_menu_id': alch.CHAR(36),
                'group_menu_name': alch.VARCHAR(50),
                'group_menu_date_cr': alch.DATETIME(),
                'group_menu_date_up': alch.DATETIME(),
                'group_menu_by_cr': alch.VARCHAR(50),
                'group_menu_by_up': alch.VARCHAR(50)
            })
        with engine.connect() as con:
            con.execute('ALTER TABLE mstrgroupmenus ADD PRIMARY KEY (group_menu_id);')
            con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_name varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_cr DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_up DATETIME NOT NULL;')
            con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_cr varchar(50) NOT NULL;')
            con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_up varchar(50) NOT NULL;')

        addLog('Group Menus','Add')
        return True, False, ''

#-------EDIT------
@app.callback(
    Output('edit-notif-groupmenus','is_open'),
    [Input('confirm-edit-groupmenus','submit_n_clicks')],
    [State('data-table-edit-groupmenus','data')]
)
def editGroupMenus(n, dataset):
    if not n:
        return False
    login_name = login.logged_login
    df_table = pd.DataFrame(dataset) 
    df_original = pd.read_sql(query2,engine)
    df_original_renamed = df_original.rename(columns = AllColumns)

    df_table.loc[(df_original_renamed["Nama Grup Menu"] != df_table["Nama Grup Menu"]),"Tanggal diperbarui"]=datetime.now()

    df_table.loc[(df_original_renamed["Nama Grup Menu"] != df_table["Nama Grup Menu"]),"Diperbarui oleh"]= login_name

    df_table_rev = df_table.rename(columns = RevAllColumns)
    tab_name = 'mstrgroupmenus'
    df_table_rev.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'group_menu_id': alch.CHAR(36),
            'group_menu_name': alch.VARCHAR(50),
            'group_menu_date_cr': alch.DATETIME(),
            'group_menu_date_up': alch.DATETIME(),
            'group_menu_by_cr': alch.VARCHAR(50),
            'group_menu_by_up': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE mstrgroupmenus ADD PRIMARY KEY (group_menu_id);')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_date_up DATETIME NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_cr varchar(50) NOT NULL;')
        con.execute('ALTER TABLE mstrgroupmenus MODIFY group_menu_by_up varchar(50) NOT NULL;')

    addLog('Group Menus', 'Edit')
    return True

@app.callback(
    Output('table-container-edit-groupmenus','children'),
    [Input('refresh-button-edit-groupmenus','n_clicks')]
)
def refEditGroupMenus(n):
    df5 = pd.read_sql(query2, engine)
    df5_renamed = df5.rename(columns = AllColumns)
    return [
        dt.DataTable(
            id='data-table-edit-groupmenus',
            columns=[
                {'name':'ID', 'id':'ID', 'editable': False},
                {'name':'Nama Grup Menu', 'id':'Nama Grup Menu', 'editable': True},
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
    Output('table-refresh-groupmenus','children'),
    [Input('refresh-page-button-groupmenus','n_clicks')]
)
def refGroupMenus(n):
    df3 = pd.read_sql(query,engine)
    df3_renamed = df3.rename(columns = notAllColumns)
    return [
        dt.DataTable(
            id='data-table-groupmenus',
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
    Output('table-container-groupmenus','children'),
    [Input('view-page-button-groupmenus','n_clicks')],
    [State('data-table-groupmenus','selected_rows'),State('data-table-groupmenus','data')]
)
def viewGroupMenus(n, row_number, dataset):
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
    viewDateCr = desire_data_df.iloc[0][2]
    viewDateUp = desire_data_df.iloc[0][3]
    viewByCr = desire_data_df.iloc[0][4]
    viewByUp = desire_data_df.iloc[0][5]

    return [
        html.H1('Lihat Group Menu', id='groupmenu-header'),
        html.Div(id='button-container-view-groupmenus',children=[
            html.A(html.Button('Kembali', id='back-view-button-groupmenus'),href='/groupmenus')
        ]),
        dbc.Spinner(children=[
            dbc.Row(
                dbc.Col([
                    html.Hr(),
                    dbc.Label('ID :', className='view-value-groupmenus'), html.Br(),
                    dbc.Label(viewID,className='view-value-groupmenus'),
                    html.Hr(),
                    dbc.Label('Nama :', className='view-value-groupmenus'),html.Br(),
                    dbc.Label(viewName,className='view-value-groupmenus'),
                    html.Hr(),
                    dbc.Label('Tanggal dibuat :', className='view-value-groupmenus'),html.Br(),
                    dbc.Label(viewDateCr,className='view-value-groupmenus'),
                    html.Hr(),
                    dbc.Label('Tanggal diperbarui :', className='view-value-groupmenus'),html.Br(),
                    dbc.Label(viewDateUp,className='view-value-groupmenus'),
                    html.Hr(),
                    dbc.Label('Dibuat oleh :', className='view-value-groupmenus'),html.Br(),
                    dbc.Label(viewByCr,className='view-value-groupmenus'),
                    html.Hr(),
                    dbc.Label('Diperbarui oleh :', className='view-value-groupmenus'),html.Br(),
                    dbc.Label(viewByUp,className='view-value-groupmenus'),
                    html.Hr(),
                ])
            , id='row-view-groupmenus')
        ], size='lg', type='grow', fullscreen=True, color='danger')
    ]

@app.server.route("/download_excel_groupmenus/")
def exportExcelGroupMenus():
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
                     attachment_filename='groupmenus.xlsx',
                     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     cache_timeout=0)
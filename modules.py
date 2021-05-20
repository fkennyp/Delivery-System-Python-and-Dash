import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
import sqlalchemy as alch
from dash.dependencies import Input, Output, State
from datetime import datetime
from dash import no_update

from app import app
from apps import login

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query3 = '''
SELECT *
FROM loghistory
'''

master = dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem('Produk',href='/products'),
                            dbc.DropdownMenuItem('Driver',href='/drivers'),
                            dbc.DropdownMenuItem('Status',href='/status'),
                            dbc.DropdownMenuItem('Kendaraan',href='/vehicles'),
                            dbc.DropdownMenuItem('Toko',href='/stores'),
                            dbc.DropdownMenuItem('Kurir',href='/couriers')
                        ],
                        nav=True,
                        in_navbar=True,
                        label='Master'
                    )

admin = dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem('User',href='/users'),
                            dbc.DropdownMenuItem('Menu',href='/menus'),
                            dbc.DropdownMenuItem('Grup Menu',href='/groupmenus'),
                            dbc.DropdownMenuItem('Grup User',href='/groupusers'),
                            dbc.DropdownMenuItem('Log',href='/log')
                        ],
                        nav=True,
                        in_navbar=True,
                        label='Admin'
                    )

transactions = dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem('Transaksi',href='/transactions'),
                            dbc.DropdownMenuItem('Cek Resi non-GAB',href='/cekresi')
                        ],
                        nav=True,
                        in_navbar=True,
                        label='Transactions'
                    )

report = dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem('Dashboard Transaksi',href='/transhome')
                        ],
                        nav=True,
                        in_navbar=True,
                        label='Report'
                    )

def navbar():
    nav = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src='assets/logogab1.png', height="50px")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="/home",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler2"),
                    dbc.Collapse(
                        dbc.Nav(
                            [
                                master,admin,transactions,report,
                                dbc.NavLink("Logout", href='/', id='logout-link', external_link=True),
                            
                            ], className="ml-auto", navbar=True, 
                        ),
                        navbar=True
                    ),
                ]
            ),
            color="dark",
            dark=True,
        )
    return nav

def navbarUser():
    nav = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src='assets/logogab1.png', height="50px")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="/user-view",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler2"),
                    dbc.Collapse(
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Daftar Transaksi", href="/user-view")),
                                dbc.NavItem(dbc.NavLink('Profil', href='/user-profile')),
                                dbc.NavLink("Logout", href='/', id='logout-link', external_link=True),
                            
                            ], className="ml-auto", navbar=True, 
                        ),
                        navbar=True
                    ),
                ]
            ),
            color="dark",
            dark=True,
        )
    return nav

def styleTable():
    return {
        'height':'100%', 
        'width':'100%',
        # 'overflowY':'auto',
        'overflowX':'auto'
    }

def styleHeader():
    return {
        'backgroundColor':'rgb(200,200,200)',
        'fontWeight':'bold',
        'width':'auto'
    }

def styleCell():
    return {
        'textAlign':'center',
        'backgroundColor':'rgb(240,240,240)',
        'minWidth': '50px', 'width': '75px', 'maxWidth': '100px',
        'fontSize':'12pt',
        
        'height':'auto',
        'whiteSpace':'normal',
    }

def addLog(menu, activity):
    login_name = login.logged_login
    df_log = pd.read_sql(query3, engine)
    log_df = [{x:''} for x in df_log.columns]
    log_df_final = {}
    for cols in log_df:
        log_df_final.update(cols)
    
    log_df_final['log_id'] = str(uuid.uuid4())
    log_df_final['log_menu_name'] = menu
    log_df_final['log_activity'] = activity
    log_df_final['log_date_cr'] = datetime.now()
    log_df_final['log_by_cr'] = login_name

    df_log = df_log.append(log_df_final, ignore_index=True)

    tab_name = 'loghistory'
    df_log.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
        dtype={
            'log_id': alch.CHAR(36),
            'log_menu_name': alch.VARCHAR(50),
            'log_activity': alch.VARCHAR(20),
            'log_date_cr': alch.DATETIME(),
            'log_by_cr': alch.VARCHAR(50)
        })
    with engine.connect() as con:
        con.execute('ALTER TABLE loghistory ADD PRIMARY KEY (log_id);')
        con.execute('ALTER TABLE loghistory MODIFY log_menu_name varchar(50) NOT NULL;')
        con.execute('ALTER TABLE loghistory MODIFY log_activity varchar(20) NOT NULL;')
        con.execute('ALTER TABLE loghistory MODIFY log_date_cr DATETIME NOT NULL;')
        con.execute('ALTER TABLE loghistory MODIFY log_by_cr varchar(50) NOT NULL;')
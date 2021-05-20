import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import hashlib
import sqlalchemy as alch
import io, flask, base64
from dash.dependencies import Input, Output, State
from datetime import datetime
from dash import no_update

from app import app
from modules import navbarUser
from apps import login

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT *
FROM mstrusers;
'''
df = pd.read_sql(query, engine)

user_profile_layout = html.Div([
    dcc.Location(id='user-profile-url', pathname='/user-profile'),
    dcc.Interval(
        id='interval-user-profile',
        disabled=False,
        interval=120 * 1000,
        n_intervals=0,
        max_intervals=-1
    ),
    navbarUser(),
    html.H1('Profil', id='user-profile-header'),
    dbc.Spinner(children=[
        dbc.Row(
            dbc.Col([
                dbc.Label(id='profile-name'),
                html.Br(),
                dbc.Label(id='profile-email'),
                dbc.FormGroup([
                        html.Hr(),
                        # password, input, confirm input
                        dbc.Label('Ganti password',id='profile-password'),
                        html.Br(),
                        dbc.Label(id='profile-password-notice'),
                        dbc.Input(placeholder='Masukkan password baru...',id='profile-password-input',type='password'),
                        html.Br(),
                        dbc.Input(placeholder='Konfirmasi password...',id='profile-password-confirm',type='password'),
                        html.Hr(),
                        html.Br(),
                        dbc.Button('Simpan',color='primary',id='profile-submit',disabled=False),
                                        
                    ] # end formgroup
                )
            ])
        , id='row-user-profile')
    ], size='lg', type='grow', fullscreen=True, color='danger')
    
])


@app.callback(
    [Output('profile-name','children'),
     Output('profile-email','children')],
    [Input('interval-user-profile','n_intervals')]
)
def user_name(n):
    name = login.logged_name
    email = login.logged_email
    return 'Masuk atas nama: '+name, 'Email: '+email

@app.callback(
    [Output('profile-password-'+x,'invalid') for x in ['input','confirm']]+\
        [Output('profile-password-notice','children')]+\
            [Output('profile-password-'+x,'value') for x in ['input','confirm']],
    [Input('profile-submit','n_clicks')],
    [State('profile-password-'+x,'value') for x in ['input','confirm']]
)
def update_password(n, NewPassword, confpass):
    if NewPassword == '':
        return True, no_update, 'Password kosong!', NewPassword, confpass
    elif confpass == '':
        return no_update, True, 'Konfirmasi password kosong!', NewPassword, confpass
    elif NewPassword != confpass:
        return True, True, 'Password dan konfirmasi password tidak sama!', NewPassword, confpass
    else:
        hashed_password = base64.b64encode(hashlib.sha1(confpass.encode('UTF-8')).digest())
        a = str(hashed_password)
        new_pass = a[2:-1]

        df = pd.read_sql(query, engine)
        name = login.logged_name

        UserData = df.loc[df['user_name'] == name]
        UserData['user_password'] = new_pass
        df.update(UserData)

        tab_name = 'mstrusers'
        df.to_sql(tab_name,con=engine, index=False, if_exists='replace', 
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

        return False, False, 'Berhasil dirubah. Anda dapat kembali ke menu utama!', '', ''
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import sqlalchemy as alch
import hashlib
import base64
from dash import no_update
from dash.dependencies import Input, Output, State
from flask import session

from auth import authenticate_user, validate_login_session
from app import app
from apps import home, products, users, drivers, status, menus, vehicles, groupmenus, groupusers, transdelivery, transhome, user_view, user_profile, log, stores, couriers, cekresi
from modules import navbarUser

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT user_id, user_login, user_name, user_password, user_role, user_email, user_location
FROM mstrusers;
'''
df = pd.read_sql(query, engine)

def getUserDetails(username):
    df = pd.read_sql(query, engine)
    dataLoc = df.loc[df['user_login'] == username] #search user based on username
    dataLocDict = dataLoc.to_dict('records')
    return dataLocDict

def role_search(user):
    dataLocDict = getUserDetails(user)
    role_list = [d['user_role'] for d in dataLocDict] #get the user_role
    role_str = str(role_list)
    role = role_str[2:-2] #user or admin
    return role

def name_search(user):
    dataLocDict = getUserDetails(user)
    name_list = [d['user_name'] for d in dataLocDict]
    name_str = str(name_list)
    name = name_str[2:-2] 
    return name

def email_search(user):
    dataLocDict = getUserDetails(user)
    email_list = [d['user_email'] for d in dataLocDict] #get the user_email
    email_str = str(email_list)
    email = email_str[2:-2]
    return email

def login_search(user):
    dataLocDict = getUserDetails(user) 
    login_list = [d['user_login'] for d in dataLocDict] #get the user_login
    login_str = str(login_list)
    login = login_str[2:-2] 
    return login

def location_search(user):
    dataLocDict = getUserDetails(user)
    location_list = [d['user_location'] for d in dataLocDict] #get the user_location
    location_str = str(location_list)
    location = location_str[2:-2] 
    return location


logged_name = ''
logged_email = ''
logged_login = ''
logged_location = ''
logged_role = ''
def setUser(name, email, login, location, role):
    global logged_name
    global logged_email
    global logged_login
    global logged_location
    global logged_role
    logged_name = name
    logged_email = email
    logged_login = login
    logged_location = location
    logged_role = role
    return logged_name, logged_email, logged_login, logged_location, logged_role

def login_layout():
    return html.Div([
        dcc.Location(id='login-url',pathname='/login',refresh=False),
        html.Div(id='page-content2', children=[
            html.Div(id='login-box', children=[
                html.H1('XYZ Delivery System', id='login-header'),

                html.Form(className='login-form', children=[
                    
                    html.Label('Username : ', className='login-form-label'),  html.Br(),
                    dcc.Input(id='login-user-input',type='text'), html.Br(),

                    html.Label('Password :  ', className='login-form-label'),html.Br(),
                    dcc.Input(id='login-pass-input',type='password'),html.Br(),
                    
                    dcc.Link(html.Button('Sign in',id='form-button-login',n_clicks=0),href='/', id='form-link-login'),
                    html.Div(id='alert')
                ])
            ])
        ])
    ])

def errorPage():
    return html.Div([
            html.P('incorrect username or password!', style={'fontWeight':'bold','fontSize':'14pt'}),
            html.A(html.Button('CLICK HERE TO LOGIN', style={'backgroundColor':'transparent','border':'none'}), href='.')
        ], style={
            'top':'50%',
            'left':'50%',
            'position':'absolute',
            'transform':'translate(-50%, -50%)',
            'textAlign':'center'
        })

def AuthPage():
    return html.Div([
            html.P('You are not authorized!', style={'fontWeight':'bold','fontSize':'14pt'}),
            html.A(html.Button('CLICK HERE TO LOGIN', style={'backgroundColor':'transparent','border':'none'}), href='/login')
        ], style={
            'top':'50%',
            'left':'50%',
            'position':'absolute',
            'transform':'translate(-50%, -50%)',
            'textAlign':'center'
        })

@app.callback(
    [Output('login-url','pathname'),Output('page-content2','children')],
    [Input('form-button-login','n_clicks')],
    [State('login-user-input','value'), State('login-pass-input','value')]
)
def auth(n, username, password):
    if n == 0:
        return no_update, no_update
    if username == '' and password == '':
        return no_update, no_update
    hashed_password = base64.b64encode(hashlib.sha1(password.encode('UTF-8')).digest())
    a = str(hashed_password)
    u_pass = a[2:-1]

    role = role_search(username)
    name = name_search(username)
    email = email_search(username)
    login = login_search(username)
    location = location_search(username)
    setUser(name, email, login, location, role)

    credentials = {'user':username, 'password':u_pass}
    if role == 'admin' or role == 'Admin' or role =='ADMIN':
        if authenticate_user(credentials):
            session['authed'] = True
            return '/home',home_layout()
        session['authed'] = False
        return no_update, errorPage()

    elif role == 'user' or role == 'User' or role == 'USER':
        if authenticate_user(credentials):
            session['authed'] = True
            return '/user-view',user_view_layout()
        session['authed'] = False
        return no_update, errorPage()

    else:
        session['authed'] = False
        return no_update, errorPage()


#----THIS SECTION IS WHERE PAGES CANNOT BE ACCESSED WITHOUT LOGIN----
@validate_login_session
def user_view_layout():
    return user_view.user_view_layout
@validate_login_session
def user_profile_layout():
    return user_profile.user_profile_layout

@validate_login_session
def log_layout():
    return log.log_layout
@validate_login_session
def cekresi_layout():
    return cekresi.cekresi_layout

@validate_login_session
def couriers_layout():
    return couriers.courier_layout
@validate_login_session
def couriers_add_layout():
    return couriers.add_layout
@validate_login_session
def couriers_edit_layout():
    return couriers.edit_layout
@validate_login_session
def couriers_del_layout():
    return couriers.delete_layout

@validate_login_session
def stores_layout():
    return stores.store_layout
@validate_login_session
def stores_add_layout():
    return stores.add_layout
@validate_login_session
def stores_edit_layout():
    return stores.edit_layout
@validate_login_session
def stores_del_layout():
    return stores.delete_layout

@validate_login_session
def home_layout():
    return home.layout
@validate_login_session
def transhome_layout():
    return transhome.transhome_layout

@validate_login_session
def prods_layout():
    return products.products_layout
@validate_login_session
def prods_add_layout():
    return products.add_layout
@validate_login_session
def prods_edit_layout():
    return products.edit_layout
@validate_login_session
def prods_del_layout():
    return products.delete_layout

@validate_login_session
def users_layout():
    return users.users_layout
@validate_login_session
def users_add_layout():
    return users.add_layout
@validate_login_session
def users_edit_layout():
    return users.edit_layout
@validate_login_session
def users_del_layout():
    return users.delete_layout

@validate_login_session
def drivers_layout():
    return drivers.drivers_layout
@validate_login_session
def drivers_add_layout():
    return drivers.add_layout
@validate_login_session
def drivers_edit_layout():
    return drivers.edit_layout
@validate_login_session
def drivers_del_layout():
    return drivers.delete_layout

@validate_login_session
def status_layout():
    return status.status_layout
@validate_login_session
def status_add_layout():
    return status.add_layout
@validate_login_session
def status_edit_layout():
    return status.edit_layout
@validate_login_session
def status_del_layout():
    return status.delete_layout

@validate_login_session
def menus_layout():
    return menus.menu_layout
@validate_login_session
def menus_add_layout():
    return menus.add_layout
@validate_login_session
def menus_edit_layout():
    return menus.edit_layout
@validate_login_session
def menus_del_layout():
    return menus.delete_layout

@validate_login_session
def groupmenus_layout():
    return groupmenus.groupmenu_layout
@validate_login_session
def groupmenus_add_layout():
    return groupmenus.add_layout
@validate_login_session
def groupmenus_edit_layout():
    return groupmenus.edit_layout
@validate_login_session
def groupmenus_del_layout():
    return groupmenus.delete_layout

@validate_login_session
def groupusers_layout():
    return groupusers.groupuser_layout
@validate_login_session
def groupusers_add_layout():
    return groupusers.add_layout
@validate_login_session
def groupusers_edit_layout():
    return groupusers.edit_layout
@validate_login_session
def groupusers_del_layout():
    return groupusers.delete_layout

@validate_login_session
def vehicles_layout():
    return vehicles.vehicle_layout
@validate_login_session
def vehicles_add_layout():
    return vehicles.add_layout
@validate_login_session
def vehicles_edit_layout():
    return vehicles.edit_layout
@validate_login_session
def vehicles_del_layout():
    return vehicles.delete_layout

@validate_login_session
def trans_layout():
    return transdelivery.transactions_layout
@validate_login_session
def trans_add_layout():
    return transdelivery.add_layout
@validate_login_session
def trans_edit_layout():
    return transdelivery.edit_layout

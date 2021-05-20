from functools import wraps
import dash_core_components as dcc
import dash_html_components as html
from flask import session
import pandas as pd
import sqlalchemy as alch
from collections import ChainMap

engine = alch.create_engine('mysql+pymysql://root:password@LAPTOP-IJL3BU6Q:3306/ptgab')
query = '''
SELECT user_login, user_password
FROM mstrusers;
'''


def authenticate_user(credentials):
    # generic authentication function returns True if user is correct and False otherwise
    df = pd.read_sql(query,engine)
    users_list = [{i:j} for i,j in zip(df['user_login'],df['user_password'])]
    users = dict(ChainMap(*users_list))

    authed = (credentials['user'] in users) and (credentials['password'] == users[credentials['user']])
    return authed


def validate_login_session(f):
    '''
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session. 
    If not, returns an error with link to the login page
    '''
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('authed',None)==True:
            return f(*args,**kwargs)

        return html.Div([
            html.H1('401 - Unauthorized'),
            html.A(dcc.Link('CLICK HERE TO LOGIN',href='/login/', style={
                                                                'textDecoration':'none',
                                                                'fontSize':'18pt'
                                                                }))
        ],style={
            'position':'absolute',
            'left':'0',
            'right':'0',
            'top':'25%',
            'width':'25%',
            'textAlign':'center',
            'margin':'auto'
        })
    return wrapper

        
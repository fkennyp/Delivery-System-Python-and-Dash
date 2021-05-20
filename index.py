import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from flask import session

from app import server
from app import app
from apps import login

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        id='page-content'
    )
])

AdminMenuList = ['/home','/transhome','/cekresi','/log',
            '/products','/products/add','/products/edit','/products/delete',
            '/couriers','/couriers/add','/couriers/edit','/couriers/delete',
            '/drivers','/drivers/add','/drivers/edit','/drivers/delete',
            '/groupmenus','/groupmenus/add','/groupmenus/edit','/groupmenus/delete',
            '/groupusers','/groupusers/add','/groupusers/edit','/groupusers/delete',
            '/menus','/menus/add','/menus/edit','/menus/delete',
            '/status','/status/add','/status/edit','/status/delete',
            '/stores','/stores/add','/stores/edit','/stores/delete',
            '/transactions','/transactions/add','/transactions/edit',
            '/users','/users/add','/users/edit','/users/delete',
            '/vehicles','/vehicles/add','/vehicles/edit','/vehicles/delete',
            ]

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def navigate_pages(pathname):
    role = login.logged_role

    if role == 'admin' or role == 'Admin' or role =='ADMIN':
        if pathname == '/user-view' or pathname == '/user-profile':
            return html.Div([html.Label('You cannot access that page!'), 
                             html.A(html.Button('Click here to back to home!', 
                                style={'backgroundColor':'transparent','border':'none'}), href='/home')
                            ], style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'})
    
    if role == 'user' or role == 'User' or role =='USER': 
        for i in AdminMenuList:
            if pathname in AdminMenuList:
                return html.Div([html.Label('You cannot access that page!'), 
                                html.A(html.Button('Click here to back to view page!', 
                                    style={'backgroundColor':'transparent','border':'none'}), href='/user-view')
                                ], style={'textAlign':'center', 'width':'50%', 'margin':'0 auto'})
        
    if pathname == '/':
        return login.login_layout()
    
    elif pathname == '/log':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.log_layout()
    elif pathname == '/cekresi':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.cekresi_layout()
    elif pathname == '/home':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.home_layout()
    elif pathname == '/transhome':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.transhome_layout()
        
    elif pathname == '/products':
        if session['authed']==False:
            return login.login_layout()
        else:
            return login.prods_layout()
    elif pathname == '/products/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.prods_add_layout()
    elif pathname == '/products/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.prods_edit_layout()
    elif pathname == '/products/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.prods_del_layout()

    elif pathname == '/users':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.users_layout()
    elif pathname == '/users/add':
        if session['authed']==False:
            return login.AuthPage()
        else:    
            return login.users_add_layout()
    elif pathname == '/users/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.users_edit_layout()
    elif pathname == '/users/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.users_del_layout()
        
    elif pathname == '/drivers':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.drivers_layout()
    elif pathname == '/drivers/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.drivers_add_layout()
    elif pathname == '/drivers/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.drivers_edit_layout()
    elif pathname == '/drivers/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.drivers_del_layout()

    elif pathname == '/status':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.status_layout()
    elif pathname == '/status/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.status_add_layout()
    elif pathname == '/status/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.status_edit_layout()
    elif pathname == '/status/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.status_del_layout()

    elif pathname == '/menus':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.menus_layout()
    elif pathname == '/menus/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.menus_add_layout()
    elif pathname == '/menus/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.menus_edit_layout()
    elif pathname == '/menus/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.menus_del_layout() 

    elif pathname == '/groupmenus':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupmenus_layout()
    elif pathname == '/groupmenus/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupmenus_add_layout()
    elif pathname == '/groupmenus/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupmenus_edit_layout()
    elif pathname == '/groupmenus/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupmenus_del_layout() 

    elif pathname == '/groupusers':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupusers_layout()
    elif pathname == '/groupusers/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupusers_add_layout()
    elif pathname == '/groupusers/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupusers_edit_layout()
    elif pathname == '/groupusers/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.groupusers_del_layout() 

    elif pathname == '/vehicles':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.vehicles_layout()
    elif pathname == '/vehicles/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.vehicles_add_layout()
    elif pathname == '/vehicles/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.vehicles_edit_layout()
    elif pathname == '/vehicles/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.vehicles_del_layout()

    elif pathname == '/transactions':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.trans_layout()
    elif pathname == '/transactions/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.trans_add_layout()
    elif pathname == '/transactions/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.trans_edit_layout()

    elif pathname == '/stores':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.stores_layout()
    elif pathname == '/stores/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.stores_add_layout()
    elif pathname == '/stores/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.stores_edit_layout()
    elif pathname == '/stores/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.stores_del_layout()

    elif pathname == '/couriers':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.couriers_layout()
    elif pathname == '/couriers/add':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.couriers_add_layout()
    elif pathname == '/couriers/edit':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.couriers_edit_layout()
    elif pathname == '/couriers/delete':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.couriers_del_layout()

    elif pathname == '/user-view':
        if session['authed']==False:
            return login.AuthPage()
        else:
            return login.user_view_layout()
    elif pathname == '/user-profile':
        if session['authed']==False:
            return login.AuthPage()
        else:   
            return login.user_profile_layout()

    elif pathname == '/login':
        return login.login_layout()
    

if __name__ == "__main__":
    # app.run_server(debug=False, port=8383, host='0.0.0.0')
    app.run_server(debug=False)
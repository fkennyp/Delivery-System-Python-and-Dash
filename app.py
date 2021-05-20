import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.SIMPLEX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.config.suppress_callback_exceptions = True
app.title = 'GAB - Delivery System'

server.config['SECRET_KEY'] = 'MIRrGUDF18HEfY7dLd9BeNaqnu2nAADW'
                              
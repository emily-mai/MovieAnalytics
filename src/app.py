import src.utils as utils
import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Movie Analytics'
app.config['suppress_callback_exceptions'] = True
dataframe = pd.DataFrame()


@app.callback(
    Output('output-container-button', 'children'),
    Input('button1', 'n_clicks'),
)
def update_output(n_clicks):
    global dataframe
    if n_clicks is not None:
        print("RECEIVED REQUEST FROM CLIENT")
        dataframe = utils.parse_csv("../data/keywords.csv", True)
        return [dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            data=dataframe.to_dict('records'),
            filter_action="native",
            sort_action="native",
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
        )]


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Movie Analytics",
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div(children=[
    navbar,
    html.Div(
        children=[
            html.H3(children='''
                Welcome! This is the homepage of our movie analytics webapp!
            '''),
            html.Hr(),
            dbc.Button('Send Request to Server ', id='button1', color="info", className="mr-1"),
            html.Div(id='output-container-button', children=[]),
            html.Hr(),

        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)

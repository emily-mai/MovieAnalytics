import src.utils as utils
import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
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
        table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            data=dataframe.to_dict('records'),
            # filter_action="native",
            # sort_action="native",
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            fixed_rows={'headers': True},
            page_size=500,
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(236,240,241)'
                }
            ],
            style_header={'backgroundColor': 'rgb(158,180,202)',
                          'fontWeight': 'bold'},
            style_cell={
                'backgroundColor': 'rgb(191,200,201)',
                'color': 'black',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in dataframe.to_dict('rows')
            ],
            tooltip_duration=None
        )
        return html.Div(id='data_table', children=table, style={'height': 800, 'width': 1000})


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
            dbc.Button('Display Table ', id='button1', color="info", className="mr-1"),
            html.Div(id='output-container-button', children=[]),
            html.Hr(),

        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )

])

if __name__ == '__main__':
    # dataframe = utils.parse_csv("../data/keywords.csv", True)
    # print(dataframe)
    app.run_server(debug=True)

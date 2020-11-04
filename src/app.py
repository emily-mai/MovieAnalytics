import src.utils as utils
import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import base64
import datetime
import io

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Movie Analytics'
app.config['suppress_callback_exceptions'] = True
metadata = utils.load_data()


def display_table(df):
    table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        css=[{'selector': '.row', 'rule': 'margin: 0'}],
        fixed_rows={'headers': True},
        # page_action='custom',
        page_size=50,
        page_current=0,
        # sort_action="native",
        row_deletable=True,
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(236,240,241)'
            }
        ],
        style_header={'backgroundColor': 'rgb(158,180,202)',
                      'fontWeight': 'bold'},
        style_table={'overflowX': 'auto'},
        style_cell={
            'backgroundColor': 'rgb(191,200,201)',
            'color': 'black',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            # 'maxWidth': 0,
            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        },
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('rows')
        ],
        tooltip_duration=None
    )
    return html.Div(id='data_table', children=table, style={'height': 800, 'width': 1000})


@app.callback(
    Output('output-container-button', "children"),
    [Input('button1', "n_clicks")],
    [State('search-bar', "value")])
def update_table(n_clicks, value):
    if n_clicks is not None:
        print(value)
        result = utils.search(metadata, query=value)
        return display_table(result)


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("edit-modal-div", "children"),
    [Input("table", "active_cell")]
)
def edit_row(active_cell):
    if active_cell is not None:
        row = active_cell.get('row')
        inputs = []
        for column in metadata.columns:
            input_id = "edit-row-input-" + column
            current_value = metadata.at[row, column]
            input_group = dbc.InputGroup(
                [
                    dbc.InputGroupAddon(column, addon_type="prepend"),
                    dbc.Input(id=input_id, value=current_value),
                ],
                className="mb-3",
                key=row
            )
            inputs.append(input_group)
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Edit"),
                dbc.ModalBody(id='edit-body', children=inputs),
                dbc.ModalFooter(dbc.Button("Submit", id="edit-submit", className="ml-auto")),
            ],
            id="edit-modal",
            is_open=True
        )
        return modal


@app.callback(
    Output("table", "data"),
    [Input("edit-submit", "n_clicks")],
    [State("edit-body", "children")]
)
def submit_edit(n_clicks, inputs):
    if n_clicks is not None:
        row_index = None
        row = []
        for input_group in inputs:
            input_dict = input_group.get('props').get('children')[1].get('props')
            input_value = input_dict.get('value')
            row_index = input_group.get('props').get('key')
            row.append(input_value)
        metadata.loc[row_index] = row
        return metadata.to_dict('records')


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


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.DataFrame()
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


app.layout = html.Div(children=[
    navbar,
    html.Div(
        children=[
            html.H3(children='''
                Welcome! This is the homepage of our movie analytics webapp!
            '''),
            html.Hr(),
            html.Div(id="edit-modal-div", children=[]),
            dbc.Input(id="search-bar", placeholder="Column name, operator, value", type="text"),
            dbc.Button('Display Table', id='button1', color="info", className="mr-1"),
            html.Div(id='output-container-button', children=[]),
            html.Hr(),

        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    ),

    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
    ])
])

if __name__ == '__main__':
    # dataframe = utils.parse_csv("../data/keywords.csv", True)
    # print(dataframe)
    app.run_server(debug=True)

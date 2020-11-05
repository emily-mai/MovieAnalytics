import src.utils as utils
import src.analysis as analysis
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
        dbc.NavItem(dbc.NavLink("Homepage", href="/")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Correlations", header=True),
                dbc.DropdownMenuItem("Rating & Budget", href="/rating-budget"),
                dbc.DropdownMenuItem("Rating & Revenue", href="/rating-revenue"),
                dbc.DropdownMenuItem("Revenue & Budget", href="/revenue-budget"),
                dbc.DropdownMenuItem("Rating & Release Time", href="/rating-release"),
                dbc.DropdownMenuItem("Popularity & Released Language", href="/popularity-language"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Average", header=True),
                dbc.DropdownMenuItem("Revenue", href="/avg-revenue"),
                dbc.DropdownMenuItem("Rating", href="/avg-rating"),
                dbc.DropdownMenuItem("Budget", href="/avg-budget"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Superlatives", header=True),
                dbc.DropdownMenuItem("Most Popular Movies", href="/popular-movies"),
                dbc.DropdownMenuItem("Most Common Keywords", href="/common-keywords"),
                dbc.DropdownMenuItem("Most Popular Release Times", href="/popular-release"),
            ],
            nav=True,
            in_navbar=True,
            label="Analytics",
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


def display_home():
    return html.Div(
        children=[
            html.H3(children='''
                Welcome!
            '''),
            html.Hr(),
            html.Div(id="edit-modal-div", children=[]),
            dbc.Row(children=[
                dbc.Col(dbc.Input(id="search-bar", placeholder="Column name, operator, value", type="text"), width=9),
                dbc.Col(dbc.Button('Search', id='button1', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "1"}),
                dbc.Col(dbc.Button('Insert', id='button2', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "2"}),
                dbc.Col(dbc.Button('Backup', id='button3', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "last"}),
            ]),
            html.Div(id='output-container-button', children=[]),
            html.Hr()
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_rating_budget():
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Budget'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_rating_revenue():
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Revenue'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_revenue_budget():
    return html.Div(
        children=[
            html.H3('Correlation between Revenue and Budget'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_rating_release_time():
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Release Time'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_popularity_released_language():
    return html.Div(
        children=[
            html.H3('Correlation between Popularity and Released Language'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_average_revenue():
    df = analysis.calculate_avg_per_genre(metadata, 'revenue')
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average revenue'],
        title='Average Revenue by Genre', color_discrete_sequence=['darkorange']*len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Revenue'),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_average_rating():
    df = analysis.calculate_avg_per_genre(metadata, 'rating')
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average rating'], range_y=[4.5, 6.5],
        title='Average Rating by Genre', color_discrete_sequence=['darkorange'] * len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Rating'),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_average_budget():
    df = analysis.calculate_avg_per_genre(metadata, 'budget')
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average budget'],
        title='Average Budget by Genre', color_discrete_sequence=['darkorange'] * len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Budget'),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_popular_movies():
    return html.Div(
        children=[
            html.H3('Most Popular Movies'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_common_keywords():
    return html.Div(
        children=[
            html.H3('Most Common Keywords'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_popular_release_time():
    return html.Div(
        children=[
            html.H3('Most Popular Release Times'),
            html.Hr(),
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)
    if pathname == "/rating-budget":
        page = display_rating_budget()
    elif pathname == "/rating-revenue":
        page = display_rating_revenue()
    elif pathname == "/revenue-budget":
        page = display_revenue_budget()
    elif pathname == "/rating-release":
        page = display_rating_release_time()
    elif pathname == "/popularity-language":
        page = display_popularity_released_language()
    elif pathname == "/avg-revenue":
        page = display_average_revenue()
    elif pathname == "/avg-rating":
        page = display_average_rating()
    elif pathname == "/avg-budget":
        page = display_average_budget()
    elif pathname == "/popular-movies":
        page = display_popular_movies()
    elif pathname == "/common-keywords":
        page = display_common_keywords()
    elif pathname == "/popular-release":
        page = display_popular_release_time()
    else:
        page = display_home()
    return page


app.layout = html.Div(children=[
    navbar,
    html.Div([
        # represents the URL bar, doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])
])

if __name__ == '__main__':
    # dataframe = utils.parse_csv("../data/keywords.csv", True)
    # print(dataframe)
    app.run_server(debug=True)

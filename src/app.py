import utils as utils
import analysis as analysis
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
import _datetime
import io
import csv
import ctypes

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
    return html.Div(id='data_table', children=table, style={'height': 800})


@app.callback(
    Output('output-container-button', "children"),
    [Input('button1', "n_clicks")],
    [State('search-bar', "value")],
)
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
    Output("insert-modal-div", "children"),
    [Input("button2", "n_clicks")]
)
def insert(n_clicks):
    #if the button has been clicked on
    if n_clicks is not None:
        inputs = []

        for column in metadata.columns:
            input_id = "insert-row-input" + column
            input_group = dbc.InputGroup(
                [
                    dbc.InputGroupAddon(column, addon_type="prepend"),
                    dbc.Input(id=input_id, placeholder="Enter data"),
                ],
                className="mb-3",
            )
            inputs.append(input_group)

        modal = dbc.Modal(
            [
                dbc.ModalHeader("Insert"),
                dbc.ModalBody(id='insert-body', children=inputs),
                # dbc.ModalFooter(dbc.Button("Done"), id="insert-done", className="ml-auto")
                dbc.ModalFooter(dbc.Button("Submit", id="insert-submit", className="ml-auto"))
            ],
            id="insert-modal",
            is_open=True
        )
        return modal


def insert_done():
    table2 = dash_table.DataTable(
        id='table2',
        columns=[{"name": i, "id": i} for i in metadata.columns],
        data=metadata.to_dict('records'),
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
            } for row in metadata.to_dict('rows')
        ],
        tooltip_duration=None
    )
    return html.Div(id='data_table2', children=table2, style={'height': 800})


@app.callback(
    Output("table2", "data"),
    [Input("insert-submit", "n_clicks")],
    [State("insert-body", "children")]
)
def submit_insert(n_clicks, inputs):
    if n_clicks is not None:
        row = []
        for input_group in inputs:
            input_dict = input_group.get('props').get('children')[1].get('props')
            input_value = input_dict.get('value')
            row.append(input_value)
        metadata.append(row)
        return metadata.to_dict('records')


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
            html.Div(id="insert-modal-div", children=[]),
            dbc.Row(children=[
                dbc.Col(dbc.Input(id="search-bar", placeholder="Column name, operator, value", type="text"), width=9),
                dbc.Col(dbc.Button('Search', id='button1', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "1"}),
                dbc.Col(dbc.Button('Insert', id='button2', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "2"}),
                dbc.Col(dbc.Button('Backup', id='button3', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "last"}),
            ]),
            dbc.Row(dbc.Col(html.Div(id='output-container-button', children=[], style={"margin-top": "10px"}), width=12)),
            dbc.Row(dbc.Col(html.Div(id='insert-submit-button', children=[], style={"margin-top": "10px"}), width=12)),
            html.Hr()
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_rating_budget():
    scatter_plot = px.scatter(metadata, x="budget", y="rating")
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Budget'),
            html.Hr(),
            dcc.Graph(figure=scatter_plot)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_rating_revenue():
    scatter_plot = px.scatter(metadata, x="revenue", y="rating")
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Revenue'),
            html.Hr(),
            dcc.Graph(figure=scatter_plot)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_revenue_budget():
    scatter_plot = px.scatter(metadata, x="budget", y="revenue")
    return html.Div(
        children=[
            html.H3('Correlation between Revenue and Budget'),
            html.Hr(),
            dcc.Graph(figure=scatter_plot)
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
    languages_votes = metadata[["spoken_languages", "rating"]]
    num_languages = []
    for i in metadata["spoken_languages"] :
        num_languages.append(len(i))
    languages_votes["num_languages"] = num_languages
    scatter_plot = px.scatter(data_frame = languages_votes, x = "num_languages", y = "rating")
    return html.Div(
        children=[
            html.H3('Correlation between Popularity and Released Language'),
            html.Hr(),
            dcc.Graph(figure=scatter_plot)
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
    genres = []
    for i in metadata["genres"]:
        for j in i:
            genres.append(j)

    pop_genres = pd.DataFrame(columns=["Genres"])
    pop_genres['Genres'] = genres
    value_counts = pop_genres['Genres'].value_counts(dropna=True, sort=True)
    pop_genres = pop_genres.value_counts().rename_axis('Genres').reset_index(name='Count')
    fig = px.bar(pop_genres, x='Genres', y='Count', title='Most Frequent Genres',
                 color_discrete_sequence=['darkorange'] * len(pop_genres)
                 )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Most Popular Movies'),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_common_keywords():
    keys = []
    for i in metadata["keywords"] :
        for j in i :
            keys.append(j)

    pop_key = pd.DataFrame(columns= ["Keys"])
    pop_key['Keys'] = keys
    value_counts = pop_key['Keys'].value_counts(dropna=True, sort=True)
    # print(value_counts)
    pop_key = pop_key.value_counts().rename_axis('Keywords').reset_index(name='Count').head(15)
    # print(pop_key)
    fig = px.bar(pop_key, x='Keywords', y='Count', title='Most Common Keywords (TOP 15)',
                 color_discrete_sequence=['darkorange'] * len(pop_key))
    return html.Div(
        children=[
            html.H3('Most Common Keywords'),
            html.Hr(),
            dcc.Graph(figure=fig)
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


#######UNDER CONSTRUCTION###############################


def my_table(df):
    table = dash_table.DataTable(
        id='test',
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
    return html.Div(id='my_table', backitup=table, style={'height': 800, 'width': 1000})


@app.callback(
    Output('output-container-button', "backitup"),
    [Input('button3', "n_clicks")],
    [State('search-bar', "value")])
def backup_data(n_clicks, value):
    if n_clicks is not None:
        df = pd.DataFrame(metadata)
        movies_list = df.values.tolist()

        # Once it has been converted, I then open a new file 'moviedata-year-month-day-hour.csv' and
        # create a csvwriter called moviewriter.
        # Then I use moviewriter to write the list to 'newFile.csv'.

        filename = datetime.datetime.now().strftime('moviedata-%Y-%m-%d-%H.csv')
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
            moviewriter = csv.writer(csvfile, delimiter=',',
                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
            moviewriter.writerows(movies_list)

        print(f"moviedata-{datetime.datetime.now():%Y-%m-%d-%H}.csv has been created.")

        ctypes.windll.user32.MessageBoxW(0, f"moviedata-{datetime.datetime.now():%Y-%m-%d-%H}.csv has been created.", "Backup",0)


#######UNDER CONSTRUCTION###############################


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

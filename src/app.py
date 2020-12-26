import src.utils as utils
import src.analysis as analysis
import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import ast
import time
import plotly.express as px
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY, "assets/stylesheet.css"])
app.title = 'Movie Analytics'
app.config['suppress_callback_exceptions'] = True
metadata = utils.load_data()

# set dataframe that is returned to '_' because not used
_, revenue_per_genre = analysis.calculate_avg_per_genre(metadata, 'revenue', per_genre=None)
_, rating_per_genre = analysis.calculate_avg_per_genre(metadata, 'rating', per_genre=None)
_, budget_per_genre = analysis.calculate_avg_per_genre(metadata, 'budget', per_genre=None)

pop_genres_count = analysis.calculate_pop_feature_count(metadata, "genres")
pop_keys_count = analysis.calculate_pop_feature_count(metadata, "keywords")
pop_companies_count = analysis.calculate_pop_feature_count(metadata, "production_companies")


def display_table(df):
    table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        css=[{'selector': '.row', 'rule': 'margin: 0'}],
        fixed_rows={'headers': True},
        virtualization=True,
        page_size=10,
        page_current=0,
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
            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        },
        # tooltip_data=[
        #     {
        #         column: {'value': str(value), 'type': 'markdown'}
        #         for column, value in row.items()
        #     } for row in df.to_dict('rows')
        # ],
        # tooltip_duration=None
    )
    return html.Div(id='data_table', children=table, style={'height': 800})


@app.callback(
    Output('search-output', "children"),
    [Input('button1', "n_clicks")],
    [State('search-bar', "value"), State('dropdown', "value")])
def search(n_clicks, search_val, dropdown_vals):
    if n_clicks is not None:
        print(search_val)
        result = utils.search(metadata, query=search_val, dropdown_vals=dropdown_vals)
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
    Output('table', 'data'),
    [Input('table', 'data_previous')],  # data_previous stores the initial dataframe only after an edit is made
    [State('table', 'data')]  # data holds the current data of the datatable
)
def row_delete(previous_data, current_data):
    # declare it global in function to modify
    global metadata, revenue_per_genre, rating_per_genre, budget_per_genre
    # if the table has not been modified
    if previous_data is None:
        dash.exceptions.PreventUpdate()
    else:
        # find difference between previous_data and current_data
        diff_row = []
        for row in previous_data + current_data:
            if row not in previous_data or row not in current_data:
                diff_row.append(row)
        # redefine the dataframe to exclude any entry with the title of the movie that is to be deleted
        metadata = metadata[metadata.original_title != diff_row[0].get('original_title')]
        # update analytics
        for row in diff_row:
            row = list(row.values())
            global revenue_per_genre, rating_per_genre, budget_per_genre, pop_genres_count, pop_keys_count
            revenue_per_genre, rating_per_genre, budget_per_genre = analysis.update_avgs_per_genre_delete(
                row, revenue_per_genre, rating_per_genre, budget_per_genre
            )
            update_start_time = time.time()
            pop_genres_count = analysis.subtract_count(pop_genres_count, row[9])
            pop_keys_count = analysis.subtract_count(pop_keys_count, row[10])
            print("Incremental Most Popular Genre Calculation Runtime: ")
            print(time.time() - update_start_time)
    return current_data


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
            current_value = str(metadata.at[row, column])
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
    Output("edit-output", "children"),
    [Input("edit-submit", "n_clicks")],
    [State("edit-body", "children")]
)
def submit_edit(n_clicks, inputs):
    if n_clicks is not None:
        row_index = None
        updated_row = []
        for input_group in inputs:
            input_dict = input_group.get('props').get('children')[1].get('props')
            input_value = input_dict.get('value')
            row_index = input_group.get('props').get('key')
            if input_value.isdigit():
                updated_row.append(int(input_value))
            elif "[" in input_value:
                updated_row.append(ast.literal_eval(input_value))
            else:
                updated_row.append(input_value)

        # assigns old_row to the row containing data of the movie before edit
        old_row = metadata.loc[row_index]
        global revenue_per_genre, rating_per_genre, budget_per_genre
        revenue_per_genre, rating_per_genre, budget_per_genre = analysis.update_avgs_per_genre_edit(
            old_row, updated_row, revenue_per_genre, rating_per_genre, budget_per_genre
        )

        before_edit_genre = metadata.loc[row_index, 'genres']  # Set before value
        after_edit_genre = updated_row[9]  # Find the appropriate genre column in row
        added_genres = list(set(after_edit_genre) - set(before_edit_genre))  # Added genres is the after - before
        analysis.add_count(pop_genres_count, added_genres)  # Update the inserted genres count
        removed_genres = list(set(before_edit_genre) - set(after_edit_genre))  # Removed genres is the before - after
        analysis.subtract_count(pop_genres_count, removed_genres)  # Decrement the count for each removed genre

        before_edit_keywords = metadata.loc[row_index, 'keywords']  # Set before value
        after_edit_keywords = updated_row[10]  # Set after value
        added_keywords = list(
            set(after_edit_keywords) - set(before_edit_keywords))  # Added genres is the after - before
        analysis.add_count(pop_keys_count, added_keywords)  # Update the inserted genres count
        removed_keywords = list(
            set(before_edit_keywords) - set(after_edit_keywords))  # Removed genres is the before - after
        analysis.subtract_count(pop_keys_count, removed_keywords)  # Decrement the count for each removed genre

        metadata.loc[row_index] = updated_row
        print("finished edit")
        updated_table = display_table(metadata)
        print("finished generating table")
        return updated_table


@app.callback(
    Output("insert-modal-div", "children"),
    [Input("button2", "n_clicks")]
)
def insert(n_clicks):
    # if the button has been clicked on
    if n_clicks is not None:
        inputs = []

        for column in metadata.columns:
            input_id = "insert-row-input" + column
            input_group = dbc.InputGroup(
                [
                    dbc.InputGroupAddon(column, addon_type="prepend"),
                    dbc.Input(id=input_id, placeholder="Enter data"),
                ],
                className="mr-1",
            )
            inputs.append(input_group)

        modal = dbc.Modal(
            [
                dbc.ModalHeader("Insert"),
                dbc.ModalBody(id='insert-body', children=inputs),
                dbc.ModalFooter(dbc.Button("Submit", id="insert-submit", className="ml-auto")),
            ],
            id="insert-modal",
            is_open=True
        )
        return modal


@app.callback(
    Output("insert-output", "children"),
    [Input("insert-submit", "n_clicks")],
    [State("insert-body", "children")]
)
def submit_insert(n_clicks, inputs):
    if n_clicks is not None:
        row = []
        for input_group in inputs:
            input_dict = input_group.get('props').get('children')[1].get('props')
            input_value = input_dict.get('value')
            # print(input_value)
            if input_value.isdigit():
                row.append(int(input_value))
            elif "[" in input_value:
                row.append(ast.literal_eval(input_value))
            else:
                row.append(input_value)

        # update analytics
        global pop_genres_count, pop_keys_count
        update_start_time = time.time()
        added_genres = row[9]  # Find the appropriate genre column in row
        pop_genres_count = analysis.add_count(pop_genres_count, added_genres)  # Update the inserted genres count
        added_keywords = row[10]
        pop_keys_count = analysis.add_count(pop_keys_count, added_keywords)
        print("Incremental Most Popular Genre Calculation Runtime: ")
        print(time.time() - update_start_time)

        global revenue_per_genre, rating_per_genre, budget_per_genre
        revenue_per_genre, rating_per_genre, budget_per_genre = analysis.update_avgs_per_genre_insert(
            row, revenue_per_genre, rating_per_genre, budget_per_genre
        )
        metadata.loc[len(metadata)] = row
        return display_table(metadata)


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
                dbc.DropdownMenuItem("Most Popular Production Companies", href="/popular-companies"),
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


def display_home():
    headers = list(metadata.columns)
    dd_options = [{"label": i, "value": i} for i in headers]
    return html.Div(
        children=[
            html.H3(children='Welcome!', style={"color": "white", "font-size": "50px", "font-weight": "bold"}),
            html.Hr(),
            html.Div(id="edit-modal-div", children=[]),
            html.Div(id="insert-modal-div", children=[]),
            dbc.Row(children=[
                dbc.Col(dcc.Dropdown(id='dropdown', options=dd_options, searchable=True, multi=True), width=3),
                dbc.Col(dbc.Input(id="search-bar", placeholder="Search...", type="text"), width=6),
                dbc.Col(dbc.Button('Search', id='button1', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "1"}),
                dbc.Col(dbc.Button('Insert', id='button2', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "2"}),
                dbc.Col(dbc.Button('Backup', id='button3', color="info", className="mr-1", block=True),
                        width={"size": 1, "order": "last"}),
            ]),
            dbc.Row(dbc.Col(html.Div(id='search-output', children=[], style={"margin-top": "10px"}), width=12)),
            dbc.Row(dbc.Col(html.Div(id='edit-output', children=[], style={"display": "none"}), width=12)),
            dbc.Row(dbc.Col(html.Div(id='insert-output', children=[], style={"display": "none"}), width=12)),
            html.Hr()
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


revenue_values = {0: '0', 200000000: '200M', 400000000: '400M', 600000000: '600M', 800000000: '800M',
                  1000000000: '1B', 1200000000: '1.2B', 1400000000: '1.4B', 1600000000: '1.6B', 1800000000: '1.8B',
                  2000000000: '2B'
                  }

budget_values = {0: '0', 50000000: '50M', 100000000: '100M', 150000000: '150M', 200000000: '200M', 250000000: '250M',
                 300000000: '300M', 350000000: '350M', 400000000: '400M'
                 }


def display_rating_budget():
    # scatter_plot = px.scatter(metadata, x="budget", y="rating")
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Budget', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(id='rating_budget_graph'),
            html.H6('Budget Range:', style={"color": "white"}),
            html.Div([
                dcc.RangeSlider(id='range_budget',
                                min=0,
                                max=400000000,
                                value=[0, 50000000],
                                marks=budget_values,
                                step=None
                                )
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('rating_budget_graph', 'figure'),
    [Input('range_budget', 'value')]
)
def update_rating_budget(budget_interval):
    new_df = metadata[(metadata['budget'] >= budget_interval[0]) & (metadata['budget'] <= budget_interval[1])]
    scatter_plot = px.scatter(data_frame=new_df, x='budget', y='rating', height=550, color_discrete_sequence=['darkorange'])
    return scatter_plot


def display_rating_revenue():
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Revenue', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(id='rating_revenue_graph'),
            html.H6('Revenue Range:', style={"color": "white"}),
            html.Div([
                dcc.RangeSlider(id='range_revenue',
                                min=0,
                                max=2000000000,
                                value=[0, 200000000],
                                marks=revenue_values,
                                step=None
                                )
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('rating_revenue_graph', 'figure'),
    [Input('range_revenue', 'value')]
)
def update_rating_revenue(revenue_interval):
    new_df = metadata[(metadata['revenue'] >= revenue_interval[0]) & (metadata['revenue'] <= revenue_interval[1])]
    scatter_plot = px.scatter(data_frame=new_df, x='revenue', y='rating', height=550, color_discrete_sequence=['darkorange'])
    return scatter_plot


def display_revenue_budget():
    return html.Div(
        children=[
            html.H3('Correlation between Revenue and Budget', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(id='revenue_budget_graph'),
            html.H6('Budget Range:', style={"color": "white"}),
            html.Div([
                dcc.RangeSlider(id='range_budget2',
                                min=0,
                                max=400000000,
                                value=[0, 50000000],
                                marks=budget_values,
                                step=None
                                )
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('revenue_budget_graph', 'figure'),
    [Input('range_budget2', 'value')]
)
def update_revenue_budget(budget_interval):
    new_df = metadata[(metadata['budget'] >= budget_interval[0]) & (metadata['budget'] <= budget_interval[1])]
    scatter_plot = px.scatter(data_frame=new_df, x='budget', y='revenue', height=550, color_discrete_sequence=['darkorange'])
    return scatter_plot


def display_rating_release_time():
    return html.Div(
        children=[
            html.H3('Correlation between Rating and Release Time', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.RadioItems(
                id='rating-time-radio',
                options=[
                   {'label': 'Linear', 'value': 'Linear'},
                   {'label': 'Scatter', 'value': 'Scatter'}
                ],
                value='Scatter',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id='rating-time-graph')
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('rating-time-graph', 'figure'),
    [Input('rating-time-radio', 'value')]
)
def update_rating_release_time(value_choice):
    if value_choice == 'Scatter':
        return px.scatter(metadata, x="release_date", y="rating", color_discrete_sequence=['darkorange'])
    else:
        return px.line(metadata, x="release_date", y="rating", color_discrete_sequence=['darkorange'])


def display_popularity_released_language():
    languages_votes = metadata[["spoken_languages", "rating"]]
    num_languages = []
    for i in metadata["spoken_languages"]:
        num_languages.append(len(i))
    languages_votes["num_languages"] = num_languages
    return html.Div(
        children=[
            html.H3('Correlation between Popularity and Released Language', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.RadioItems(id='popularity-language-radio',
                           options=[
                               {'label': 'Linear', 'value': 'Linear'},
                               {'label': 'Scatter', 'value': 'Scatter'}
                           ],
                           value='Scatter',
                           labelStyle={'display': 'inline-block'}
                           ),

            dcc.Graph(id='popularity-language-graph')
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('popularity-language-graph', 'figure'),
    [Input('popularity-language-radio', 'value')]
)
def update_popularity_released_language(chosen_value):
    languages_votes = metadata[["spoken_languages", "rating"]]
    num_languages = []
    for i in metadata["spoken_languages"]:
        num_languages.append(len(i))
    languages_votes["num_languages"] = num_languages

    if chosen_value == 'Scatter':
        return px.scatter(data_frame=languages_votes, x="num_languages", y="rating", color_discrete_sequence=['darkorange'])
    else:
        return px.line(data_frame=languages_votes, x="num_languages", y="rating", color_discrete_sequence=['darkorange'])


def display_average_revenue():
    df, _ = analysis.calculate_avg_per_genre(metadata, 'revenue', revenue_per_genre)
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average revenue'],
        title='Average Revenue by Genre', color_discrete_sequence=['darkorange']*len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Revenue', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig, id='avg revenue'),
            html.H6('Sort: High to Low'),
            html.Div([
                html.Button('View in New Tab', id='SortAvgRev'),
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('avg revenue', 'fig'),
    [Input('SortAvgRev', 'n_clicks')]
)
def revenue_high_to_low(n_clicks):
    if n_clicks is not None:
        df, _ = analysis.calculate_avg_per_genre(metadata, 'revenue', revenue_per_genre)
        fig = px.bar(
            data_frame=df, x=df['genre'], y=df['average revenue'],
            title='Average Revenue by Genre', color_discrete_sequence=['darkorange'] * len(df)
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        return fig.show()


def display_average_rating():
    df, _ = analysis.calculate_avg_per_genre(metadata, 'rating', rating_per_genre)
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average rating'],
        title='Average Rating by Genre', color_discrete_sequence=['darkorange'] * len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Rating', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig, id='avg rating'),
            html.H6('Sort: High to Low'),
            html.Div([
                html.Button('View in New Tab', id='SortAvgRat'),
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('avg rating', 'fig'),
    [Input('SortAvgRat', 'n_clicks')]
)
def rating_high_to_low(n_clicks):
    if n_clicks is not None:
        df, _ = analysis.calculate_avg_per_genre(metadata, 'rating', rating_per_genre)
        fig = px.bar(
            data_frame=df, x=df['genre'], y=df['average rating'],
            title='Average Rating by Genre', color_discrete_sequence=['darkorange'] * len(df)
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        return fig.show()


def display_average_budget():
    df, _ = analysis.calculate_avg_per_genre(metadata, 'budget', budget_per_genre)
    fig = px.bar(
        data_frame=df, x=df['genre'], y=df['average budget'],
        title='Average Budget by Genre', color_discrete_sequence=['darkorange'] * len(df)
    )
    fig.update_layout(title_x=0.5)
    return html.Div(
        children=[
            html.H3('Average Budget', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig, id="avg budget"),
            html.H6('Sort: High to Low'),
            html.Div([
                html.Button('View in New Tab', id='SortAvgBud'),
            ])
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


@app.callback(
    Output('avg budget', 'fig'),
    [Input('SortAvgBud', 'n_clicks')]
)
def rating_high_to_low(n_clicks):
    if n_clicks is not None:
        df, _ = analysis.calculate_avg_per_genre(metadata, 'budget', budget_per_genre)
        fig = px.bar(
            data_frame=df, x=df['genre'], y=df['average budget'],
            title='Average Budget by Genre', color_discrete_sequence=['darkorange'] * len(df)
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        return fig.show()


def display_popular_movies():
    fig = px.bar(x=list(pop_genres_count.keys()), y=list(pop_genres_count.values()), title='Most Frequent Genres',
                 color_discrete_sequence=['darkorange'] * len(pop_genres_count)
                 )
    fig.update_layout(title_x=0.5, xaxis_title="genre", yaxis_title="count")
    return html.Div(
        children=[
            html.H3('Most Popular Movies', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_common_keywords():
    fig = px.bar(x=list(pop_keys_count.keys())[0:15], y=list(pop_keys_count.values())[0:15],
                 title='Most Common Keywords (TOP 15)', color_discrete_sequence=['darkorange'] * 15)
    fig.update_layout(xaxis_title="keyword", yaxis_title="count")
    return html.Div(
        children=[
            html.H3('Most Common Keywords', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig)
        ],
        style={"margin-left": "5%", "margin-right": "5%", "margin-top": "5%"}
    )


def display_popular_production_companies():
    fig = px.bar(x=list(pop_companies_count.keys())[0:10], y=list(pop_companies_count.values())[0:10],
                 title='Most Popular Production Companies (TOP 10)', color_discrete_sequence=['darkorange'] * 10)
    fig.update_layout(xaxis_title="production_companies", yaxis_title="count")
    return html.Div(
        children=[
            html.H3('Most Popular Production Companies', style={"color": "white", "font-weight": "bold"}),
            html.Hr(),
            dcc.Graph(figure=fig)
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
    elif pathname == "/popular-companies":
        page = display_popular_production_companies()
    else:
        page = display_home()
    return page


app.layout = html.Div(
    children=[
        navbar,
        html.Div([
            # represents the URL bar, doesn't render anything
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])
    ],
    style={
        "background-image": "url(https://static.vecteezy.com/system/resources/previews/000/157/184/original/retro-movie-cinema-vector-background.jpg)",
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-size": "cover",
        "position": "fixed",
        "min-height": "100%",
        "min-width": "100%"
    }
)

if __name__ == '__main__':
    app.run_server(debug=True)

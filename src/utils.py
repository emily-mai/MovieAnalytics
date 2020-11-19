import pandas as pd
import numpy as np
import re
# this line can be commented out --> tells run time of for loops
from tqdm import tqdm


# csv parser function
def parse_csv(filepath, contains_header=False):
    """
    :param filepath: location of csv data file
    :param contains_header: flag for whether csv has headers or not
    :return: dataframe object of csv data
    """
    # open csv file with open() and call it file
    with open(filepath, 'r', encoding="utf8") as file:
        data = []
        headers = []
        # case for when file contains headers
        if contains_header:
            # reading first line with readline()
            # splitting line (separated by commas) to get each column header
            headers = file.readline().strip('\n').split(',')
        # use for loop to read in rest of file
        # split data into corresponding columns using regex expression
        for line in file:
            line = line.strip('\n')
            words = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))', line)
            row = []
            for word in words:
                if word.isdigit():
                    row.append(int(word))
                else:
                    row.append(word)
            data.append(row)
            # break
    # case for when file contains header when creating dataframe
    if contains_header:
        dataframe = pd.DataFrame(data, columns=headers)
    else:
        dataframe = pd.DataFrame(data)
    # print(dataframe)
    return dataframe


# declare comparison operators
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


# function to process search inputs
def split_filter_part(filter_part):
    """
    :param filter_part: string formatted as "column operator value"
    :return: filter_part formatted as list of strings, if contains operator else return empty list
    """
    # only split if operator is in the search input
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                # clean up strings
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', '`'):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value
    return [None] * 3


def load_data():
    meta = parse_csv("../data/movies_metadata.csv", True).drop_duplicates('id')
    kwords = parse_csv("../data/keywords.csv", True).drop_duplicates('id')

    meta.set_index('id', inplace=True)
    kwords.set_index('id', inplace=True)

    meta = pd.concat([meta, kwords], axis=1, join='inner').reset_index()
    meta = meta.drop(['adult', 'belongs_to_collection', 'imdb_id', 'title', 'video', 'id'], axis=1)
    meta = clean_dataframe(meta,
                           ['genres', 'keywords', 'production_companies', 'production_countries', 'spoken_languages'])
    meta = meta.rename(columns={"vote_average": "rating"})
    return meta


def clean_dataframe(df, columns):
    """
    :param df: dataframe object to clean
    :param columns: list of df columns to clean (i.e. keywords, genres)
    :return: cleaned up version of dataframe
    """
    for column in columns:
        keywords_list = df[column]
        clean = []
        for string in keywords_list:
            new_row = []
            if string is not None:
                try:
                    row = list(eval(string.strip('"')))
                except SyntaxError:
                    row = []
                for dictionary in row:
                    dictionary_value = dictionary.get('name')
                    new_row.append(dictionary_value)
            clean.append(new_row)
        df.drop(columns=[column], inplace=True)
        df[column] = pd.Series(clean)
    return df


def search(dataframe, query):
    """
    :param dataframe: dataframe object to perform search on
    :param query: query string to filter data
    :return: dataframe of query results
    """
    if query is not None:
        # split multiple queries and process sequentially
        filtering_expressions = query.split(' && ')
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)
            # print(col_name, operator, filter_value)
            # these operators match pandas series operator method names
            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                dataframe = dataframe.loc[getattr(dataframe[col_name], operator)(filter_value)]
            elif operator == 'contains':
                filter_value = {filter_value}
                isfilter_value = filter_value.issubset
                dataframe[col_name] = [[] if x is np.NaN else x for x in dataframe[col_name]]
                values = dataframe[col_name].values.tolist()
                dataframe = dataframe[[isfilter_value(val) for val in values]]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]
    return dataframe

def pop_genre_table(df):
    genres = []
    for i in df["genres"]:
        for j in i:
            genres.append(j)

    pop_genres = pd.DataFrame(columns=["Genres"])
    pop_genres['Genres'] = genres
    value_counts = pop_genres['Genres'].value_counts(dropna=True, sort=True)
    pop_genres = pop_genres.value_counts().rename_axis('Genres').reset_index(name='Count')

    return pop_genres

def pop_keywords_table(df):
    keys = []
    for i in df["keywords"] :
        for j in i :
            keys.append(j)

    pop_key = pd.DataFrame(columns= ["Keys"])
    pop_key['Keys'] = keys
    value_counts = pop_key['Keys'].value_counts(dropna=True, sort=True)
    # print(value_counts)
    pop_key = pop_key.value_counts().rename_axis('Keywords').reset_index(name='Count')
    
    return pop_key

def insert_genre_count(df, genres):
    for row in df.rows:
        for i in genres:
            if df.at[row, 0] == i:
                df.at[row, 1] = df.at[row, 1] + 1

def insert_keyword_count(df, keywords):
    for row in df.rows:
        for i in keywords:
            if df.at[row, 0] == i:
                df.at[row, 1] = df.at[row, 1] + 1

def remove_genre_count(df, genres):
    for row in df.rows:
        for i in genres:
            if df.at[row, 0] == i:
                df.at[row, 1] = df.at[row, 1] - 1

def remove_keyword_count(df, keywords):
    for row in df.rows:
        for i in keywords:
            if df.at[row, 0] == i:
                df.at[row, 1] = df.at[row, 1] - 1



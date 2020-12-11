import pandas as pd
import re


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
                if word.replace('.', '', 1).isdigit():
                    row.append(float(word))
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
    meta = meta.drop(['adult', 'belongs_to_collection', 'imdb_id', 'title', 'video', 'id', 'homepage', 'poster_path',
                      'status', 'original_language', 'popularity'], axis=1)
    meta = clean_dataframe(meta,
                           ['genres', 'keywords', 'production_companies', 'production_countries', 'spoken_languages'])
    meta = meta.rename(columns={"vote_average": "rating"})
    meta = meta[meta['rating'] != 0]
    meta = meta[meta['budget'] != 0]
    meta = meta[meta['revenue'] != 0]
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


def search(dataframe, query, dropdown_vals):
    """
    :param dataframe: dataframe object to perform search on
    :param query: query string to filter
    :param dropdown_vals: list of column headers
    :return: dataframe of query results
    """
    result = pd.DataFrame()
    if query is not None and dropdown_vals is not None:
        for header in dropdown_vals:
            series = dataframe[header].dropna()
            if isinstance(series[0], list):
                df_filtered = dataframe[pd.DataFrame(series.tolist()).isin([query]).values]
                result = result.append(df_filtered)
            if isinstance(series[0], str) \
                    and not query.replace('.', '', 1).isdigit() \
                    and not series[0].replace('.', '', 1).isdigit():
                df_filtered = dataframe[series.str.contains(query)]
                result = result.append(df_filtered)
            if isinstance(series[0], float) and query.replace('.', '', 1).isdigit():
                bools = [float(query) == x if x is not None else False for x in dataframe[header]]
                df_filtered = dataframe[bools]
                result = result.append(df_filtered)
    return result

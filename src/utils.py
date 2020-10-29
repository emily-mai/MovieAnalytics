import pandas as pd
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
        for line in tqdm(file):
            line = line.strip('\n')
            words = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))', line)
            data.append(words)
    # case for when file contains header when creating dataframe
    if contains_header:
        dataframe = pd.DataFrame(data, columns=headers)
    else:
        dataframe = pd.DataFrame(data)
    print(dataframe)
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
            print(col_name, operator, filter_value)
            # these operators match pandas series operator method names
            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                dataframe = dataframe.loc[getattr(dataframe[col_name], operator)(filter_value)]
            elif operator == 'contains':
                dataframe = dataframe.loc[dataframe[col_name].str.contains(filter_value)]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]
    return dataframe


# def update(dataframe, index, column, value):
#     """
#     :param dataframe: dataframe object to perform update on
#     :param index: data index that user wants to edit
#     :param column: data column that the user wants to edit
#     :param value: user input for editing
#     """
#     # dataframe parameter to get access to movie listings
#     dataframe.at[index, column] = value
#     return dataframe

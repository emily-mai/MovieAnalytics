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

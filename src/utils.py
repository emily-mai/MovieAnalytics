import pandas as pd
import re
from tqdm import tqdm


# csv parser function
def parse_csv(filepath, contains_header=False):
    with open(filepath, 'r', encoding="utf8") as file:
        data = []
        headers = []
        if contains_header:
            headers = file.readline().strip('\n').split(',')
        for line in tqdm(file):
            line = line.strip('\n')
            words = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))', line)
            data.append(words)
    if contains_header:
        dataframe = pd.DataFrame(data, columns=headers)
    else:
        dataframe = pd.DataFrame(data)
    print(dataframe)
    return dataframe

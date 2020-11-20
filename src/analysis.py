import pandas as pd
import ast


# function to calculate average X per genre
def calculate_avg_per_genre(dataframe, col, per_genre):
    """
    :param dataframe: dataframe object to find averages
    :param col: column to calculate average
    :param per_genre: dictionary of the count and sum per genre
    :return: dataframe of averages per genre and dictionaries of the count and sum per genre
    """
    # case that total and count have not been calculated before
    if per_genre is None:
        per_genre = {}  # {"horror": (sum, count), "comedy": (sum ,count), ...}
        for genres, feature in zip(dataframe['genres'], dataframe[col]):
            try:
                feature = float(feature)
            except (ValueError, TypeError):
                feature = 0
            for genre in genres:
                if genre in per_genre:
                    feature_sum, count = per_genre.get(genre)
                    per_genre[genre] = (feature_sum + feature, count + 1)
                else:
                    per_genre[genre] = (feature, 1)
    # calculates average (incremental case will always run below)
    averages = {}
    for genre in per_genre:
        sum, count = per_genre.get(genre)
        averages[genre] = sum / count
    temp = 'average ' + col
    df = pd.DataFrame(list(averages.items()), columns=['genre', temp])
    return df, per_genre


# function to update count and sum dictionaries when a movie is inserted
def update_avgs_per_genre_insert(movie, revenue_per_genre, rating_per_genre, budget_per_genre):
    """
    :param movie: row containing data of movie after an insert
    :param revenue_per_genre: dictionary of the count and sum by genre for revenue
    :param rating_per_genre: dictionary of the count and sum by genre for rating
    :param budget_per_genre: dictionary of the count and sum by genre for budget
    :return: dictionaries of the count and sum by genre for revenue, rating, and budget
    """
    genre_val = movie[14]
    revenue_val = int(movie[8])
    budget_val = int(movie[0])
    rating_val = float(movie[12])
    # for every genre, increment count and add value of newly added item to sum for revenue, rating, budget
    for genre in genre_val:
        # print(genre)
        if genre in revenue_per_genre:
            feature_sum, count = revenue_per_genre.get(genre)
            revenue_per_genre[genre] = (feature_sum + revenue_val, count + 1)
        if genre in rating_per_genre:
            feature_sum, count = rating_per_genre.get(genre)
            rating_per_genre[genre] = (feature_sum + rating_val, count + 1)
        if genre in budget_per_genre:
            feature_sum, count = budget_per_genre.get(genre)
            budget_per_genre[genre] = (feature_sum + budget_val, count + 1)
        else:  # new genre, not found in current data
            revenue_per_genre[genre] = (revenue_val, 1)
            rating_per_genre[genre] = (rating_val, 1)
            budget_per_genre[genre] = (budget_val, 1)
    return revenue_per_genre, rating_per_genre, budget_per_genre


# function to update sum and count dictionaries when a movie is removed
def update_avgs_per_genre_delete(movie, revenue_per_genre, rating_per_genre, budget_per_genre):
    """
    :param movie: row containing data of a movie
    :param revenue_per_genre: dictionary of the count and sum by genre for revenue
    :param rating_per_genre: dictionary of the count and sum by genre for rating
    :param budget_per_genre: dictionary of the count and sum by genre for budget
    :return: dictionaries of the updated count and sum by genre for revenue, rating, and budget after removal of old data
    """
    genre_val = movie[14]
    revenue_val = int(movie[8])
    budget_val = int(movie[0])
    rating_val = float(movie[12])
    # for every genre, decrement count and the subtract value of old item from sum for revenue, rating, budget
    for genre in genre_val:
        if genre in revenue_per_genre:
            feature_sum, count = revenue_per_genre.get(genre)
            revenue_per_genre[genre] = (feature_sum - revenue_val, count - 1)
        if genre in rating_per_genre:
            feature_sum, count = rating_per_genre.get(genre)
            rating_per_genre[genre] = (feature_sum - rating_val, count - 1)
        if genre in budget_per_genre:
            feature_sum, count = budget_per_genre.get(genre)
            budget_per_genre[genre] = (feature_sum - budget_val, count - 1)
    return revenue_per_genre, rating_per_genre, budget_per_genre


# function to update sum and count dictionaries after an edit is made
def update_avgs_per_genre_edit(old_movie, updated_movie, revenue_per_genre, rating_per_genre, budget_per_genre):
    """
    :param old_movie: row containing data of the movie before edit
    :param updated_movie: row containing data of the movie after edit
    :param revenue_per_genre: dictionary of the count and sum by genre for revenue
    :param rating_per_genre: dictionary of the count and sum by genre for rating
    :param budget_per_genre: dictionary of the count and sum by genre for budget
    :return: dictionaries of the updated count and sum by genre for revenue, rating, and budget after removal of old data
    """
    # once edit is made, remove old data and update the count and sum
    deleted_result = update_avgs_per_genre_delete(old_movie, revenue_per_genre, rating_per_genre, budget_per_genre)
    # add the new data and update the count and sum
    edited_result = update_avgs_per_genre_insert(updated_movie, deleted_result[0], deleted_result[1], deleted_result[2])
    return edited_result[0], edited_result[1], edited_result[2]


def calculate_pop_feature_count(df, feature_name):
    features = []
    for i in df[feature_name]:
        for j in i:
            features.append(j)
    pop_features = pd.DataFrame(columns=[feature_name])
    pop_features[feature_name] = features
    temp = pop_features.value_counts().rename_axis(feature_name).reset_index(name='count', drop=False)
    temp = temp.set_index(feature_name).to_dict()['count']
    return temp


def add_count(dictionary, features):
    for i in features:
        if i in dictionary:
            count = dictionary.get(i)
            dictionary[i] = count + 1
        else:
            dictionary[i] = 1
    return dictionary


def subtract_count(dictionary, features):
    for i in features:
        if i in dictionary:
            count = dictionary.get(i)
            dictionary[i] = count - 1
    return dictionary


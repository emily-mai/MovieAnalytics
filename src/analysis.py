import pandas as pd
import ast


def calculate_avg_per_genre(dataframe, col, per_genre):
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
    averages = {}
    for genre in per_genre:
        sum, count = per_genre.get(genre)
        averages[genre] = sum / count
    temp = 'average ' + col
    df = pd.DataFrame(list(averages.items()), columns=['genre', temp])
    return df, per_genre


def update_avgs_per_genre(movie, revenue_per_genre, rating_per_genre, budget_per_genre):
    genre_val = movie[14]
    revenue_val = movie[8]
    budget_val = movie[0]
    rating_val = movie[12]
    for genre in genre_val:
        print(genre)
        if genre in revenue_per_genre:
            feature_sum, count = revenue_per_genre.get(genre_val)
            revenue_per_genre[genre_val] = (feature_sum + revenue_val, count + 1)
        if genre in rating_per_genre:
            feature_sum, count = rating_per_genre.get(genre_val)
            rating_per_genre[genre_val] = (feature_sum + rating_val, count + 1)
        if genre in budget_per_genre:
            feature_sum, count = budget_per_genre.get(genre_val)
            budget_per_genre[genre_val] = (feature_sum + budget_val, count + 1)
        else:  # new genre, not found in current data
            revenue_per_genre[genre] = (revenue_val, 1)
            rating_per_genre[genre] = (rating_val, 1)
            budget_per_genre[genre] = (budget_val, 1)
    return revenue_per_genre, rating_per_genre, budget_per_genre


# def genre_analytics(metadata) :
#     """
#     :param dataframe: dataframe object to perform search/analytics on
#     :return: display graph
#     """
#     # Extract genres from the dataframe to build analytics
#     # dataframe["genres"] = dataframe["genres"].astype('str')
#     genres = []
#     for i in metadata["genres"] :
#         for j in i :
#             genres.append(j)
#
#     pop_genres = pd.DataFrame(columns= ["Genres"])
#     pop_genres['Genres'] = genres
#     value_counts = pop_genres['Genres'].value_counts(dropna=True, sort=True)
#     # print(value_counts)
#     pop_genres = pop_genres.value_counts().rename_axis('Genres').reset_index(name='Count')
#     # print(pop_genres)
#     # fig = px.bar(pop_genres, x='Genres', y='Count')
#     # fig.show()


# def popular_actors(metadata) :
#     keys = []
#     for i in metadata["keywords"] :
#         for j in i :
#             keys.append(j)

#     pop_key = pd.DataFrame(columns= ["Keys"])
#     pop_key['Keys'] = keys
#     value_counts = pop_key['Keys'].value_counts(dropna=True, sort=True)
#     # print(value_counts)
#     pop_key = pop_key.value_counts().rename_axis('Keywords').reset_index(name='Count')
#     print(pop_key)
#     fig = px.bar(pop_key, x='Keywords', y='Count')
#     fig.show()


# def popular_keywords(metadata) :
#
#     keys = []
#     for i in metadata["keywords"] :
#         for j in i :
#             keys.append(j)
#
#     pop_key = pd.DataFrame(columns= ["Keys"])
#     pop_key['Keys'] = keys
#     value_counts = pop_key['Keys'].value_counts(dropna=True, sort=True)
#     # print(value_counts)
#     pop_key = pop_key.value_counts().rename_axis('Keywords').reset_index(name='Count')
#     # print(pop_key)
#     fig = px.bar(pop_key, x='Keywords', y='Count')
#     fig.show()
#
#
# def votes_languages(metadata) :
#     languages_votes = metadata[["spoken_languages", "rating"]]
#     num_languages = []
#     for i in metadata["spoken_languages"] :
#         num_languages.append(len(i))
#     languages_votes["num_languages"] = num_languages
#     # print(languages_votes)
#     scatterPlot = px.scatter(data_frame = languages_votes, x = "num_languages", y = "rating")
#     scatterPlot.show()

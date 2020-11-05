import pandas as pd


def calculate_avg_per_genre(dataframe, col):
    per_genre = {}  # {"horror": (sum, count), "comedy": (sum ,count), ...}
    for genres, feature in zip(dataframe['genres'], dataframe[col]):
        try:
            feature = float(feature)
        except (ValueError, TypeError):
            feature = 0
        for genre in genres:
            if genre in per_genre:
                feature_sum, count = per_genre.get(genre)
                feature_sum += feature
                count += 1
                per_genre[genre] = (feature_sum, count)
            else:
                per_genre[genre] = (feature, 1)
    averages = {}
    for genre in per_genre:
        sum, count = per_genre.get(genre)
        averages[genre] = sum / count
    temp = 'average ' + col
    df = pd.DataFrame(list(averages.items()), columns=['genre', temp])
    return df


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


# def budget_revenue(metadata) :
#     """
#     :param dataframe: dataframe object to perform search/analytics on
#     :return: display graph
#     """
#     scatterPlot = px.scatter(metadata, x = "budget", y = "revenue")
#     scatterPlot.show()
#
#
# def budget_rating(metadata) :
#     """
#     :param dataframe: dataframe object to perform search/analytics on
#     :return: display graph
#     """
#     scatterPlot = px.scatter(metadata, x = "budget", y = "rating")
#     scatterPlot.show()
#
#
# def revenue_rating(metadata) :
#     """
#     :param dataframe: dataframe object to perform search/analytics on
#     :return: display graph
#     """
#     scatterPlot = px.scatter(metadata, x = "revenue", y = "rating")
#     scatterPlot.show()

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
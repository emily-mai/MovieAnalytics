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
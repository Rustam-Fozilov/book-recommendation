import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import book_service

books_filename = 'books.csv'
ratings_filename = 'ratings.csv'

# import csv data into dataframes
df_books = pd.read_csv(
    books_filename,
    encoding="ISO-8859-1",
    sep=";",
    header=0,
    names=['isbn', 'title', 'author', 'year', 'publisher', 'image-url-s', 'image-url-m', 'image-url-l'],
    usecols=['isbn', 'title', 'author', 'year', 'publisher', 'image-url-s', 'image-url-m', 'image-url-l'],
    dtype={'isbn': 'str', 'title': 'str', 'author': 'str', 'year': 'str', 'publisher': 'str', 'image-url-s': 'str',
           'image-url-m': 'str', 'image-url-l': 'str'}
)

df_ratings = pd.read_csv(
    ratings_filename,
    encoding="ISO-8859-1",
    sep=";",
    header=0,
    names=['user', 'isbn', 'rating'],
    usecols=['user', 'isbn', 'rating'],
    dtype={'user': 'int32', 'isbn': 'str', 'rating': 'float32'}
)

df = df_ratings[["user", "rating"]] \
    .groupby(["user"]) \
    .count() \
    .reset_index()

df['rating_log10'] = np.log10(df['rating'])
# df.plot.scatter(x="user", y="rating_log10")


dfb = df_ratings.groupby(["isbn"]).count().reset_index()
good_books = dfb.loc[dfb["rating"] >= 100]["isbn"]

# books contains those have no less than 100 ratings
good_books = df_books.loc[df_books["isbn"].isin(good_books)]

dfu = df_ratings[["user", "rating"]] \
    .groupby(["user"]) \
    .count() \
    .reset_index()

good_users = dfu.loc[dfu["rating"] >= 200]["user"]

df = df_ratings.loc[df_ratings["user"].isin(good_users)]
df = df.loc[df["isbn"].isin(good_books["isbn"])]

# pivot ratings into book features
df_book_features = df.pivot(
    index='isbn',
    columns='user',
    values='rating'
).fillna(0)

# convert dataframe of book features to scipy sparse matrix
# this part requires a lot of memory!
mat_book_features = csr_matrix(df_book_features.values)

model = NearestNeighbors(metric='cosine')
model.fit(mat_book_features)


def get_book(isbn):
    try:
        book = good_books.loc[good_books["isbn"] == isbn]
    except KeyError as e:
        return {"error": f"Book isbn '{isbn}' does not exist"}

    if book.empty:
        return {"error": f"Book isbn '{isbn}' not found"}

    return book_service.transform_data(book)


def search_books(query, field="title"):
    if field not in good_books.columns:
        return {"error": f"Invalid field '{field}'"}

    results = good_books.loc[good_books[field].str.contains(query, case=False, na=False)]

    if results.empty:
        return {"error": f"No books found matching '{query}' in field '{field}'"}

    return results.to_dict(orient="records")


def get_recommends(isbn=""):
    try:
        book = good_books.loc[good_books["isbn"] == isbn]
    except KeyError as e:
        return {"error": f"Book isbn '{isbn}' does not exist"}

    if book.empty:
        return {"error": f"Book isbn '{isbn}' not found"}

    b = df_book_features.loc[df_book_features.index.isin(book["isbn"])]
    distance, indice = model.kneighbors([x for x in b.values], n_neighbors=51)

    distance = distance[0][1:]
    indice = indice[0][1:]

    # Ensure valid_indices does not exceed the length of df_book_features
    max_index = len(df_book_features) - 1

    # Initialize valid_indices to avoid UnboundLocalError
    valid_indices = [i for i in indice if i <= max_index]

    if not valid_indices:
        return {"error": "No valid indices found for recommendations"}

    recommendations = [
        {
            "title": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["title"].values[0],
            "isbn": df_book_features.index[i],
            "author": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["author"].values[0],
            "year": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["year"].values[0],
            "publisher": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["publisher"].values[0],
            # "image_url_s": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["image-url-s"].values[0],
            "image_url_m": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["image-url-m"].values[0],
            "image_url_l": df_books.loc[df_books["isbn"] == df_book_features.index[i]]["image-url-l"].values[0],
            "distance": str(distance[j]),
        }
        for j, i in enumerate(valid_indices)
    ]

    return recommendations

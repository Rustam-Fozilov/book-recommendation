from typing import Union
from fastapi import FastAPI
import uvicorn
import knn

app = FastAPI()


def transformed_books():
    # Transforming the data
    transformed_data = []
    keys = knn.good_books.head(10)["isbn"].keys()

    for key in keys:
        book = {
            "isbn": knn.good_books.head(10)["isbn"][key],
            "title": knn.good_books.head(10)["title"][key],
            "author": knn.good_books.head(10)["author"][key],
            "year": knn.good_books.head(10)["year"][key],
            "publisher": knn.good_books.head(10)["publisher"][key],
            "image-url-s": knn.good_books.head(10)["image-url-s"][key],
            "image-url-m": knn.good_books.head(10)["image-url-m"][key],
            "image-url-l": knn.good_books.head(10)["image-url-l"][key],
        }
        transformed_data.append(book)

    return transformed_data


@app.get("/")
def read_root():
    return {
        "data": transformed_books()
    }


@app.get("/recommendation/{isbn}")
def read_item(isbn: str):
    return knn.get_recommends(isbn)

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)

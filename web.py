from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import knn

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def transformed_books():
    # Transforming the data
    transformed_data = []
    original_books = knn.good_books.head(8)
    keys = knn.good_books.head(8)["isbn"].keys()

    for key in keys:
        book = {
            "isbn": original_books["isbn"][key],
            "title": original_books["title"][key],
            "author": original_books["author"][key],
            "year": original_books["year"][key],
            "publisher": original_books["publisher"][key],
            "image_url_s": original_books["image-url-s"][key],
            "image_url_m": original_books["image-url-m"][key],
            "image_url_l": original_books["image-url-l"][key],
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

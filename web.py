from typing import Union
from fastapi import FastAPI
import uvicorn
import knn


app = FastAPI()


@app.get("/")
def read_root():
    return {
        "data": knn.good_books.head()
    }


@app.get("/recommend/{isbn}")
def read_item(isbn: str):
    return knn.get_recommends(isbn)


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# if __name__ == '__main__':
#     uvicorn.run(app, host='127.0.0.1', port=8000)

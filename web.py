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


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)

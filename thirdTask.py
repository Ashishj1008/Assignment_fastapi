from fastapi import FastAPI

from math import sqrt

app = FastAPI()


@app.get("/distance")
def calculate_distance(x1: float, y1: float, x2: float, y2: float):
    distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return {"distance": distance}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=5000)

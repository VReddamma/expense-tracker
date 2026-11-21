from fastapi import FastAPI

app = FastAPI(title="TaskFlow API")


@app.get("/")
def root():
    return {"message": "Welcome to the app"}

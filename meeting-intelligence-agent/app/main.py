from fastapi import FastAPI

from app.routes.meeting_routes import router

app = FastAPI(
    title="Meeting Intelligence Agent"
)

app.include_router(router)


@app.get("/")
def home():

    return {
        "message":
        "Meeting Intelligence Agent Running"
    }
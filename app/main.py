from fastapi import FastAPI
from app.api.routers.muscles import muscles_router
from app.api.routers.exercises import exercises_router
from app.api.routers.splits import splits_router

app = FastAPI()

# ✅ Register Routers
app.include_router(muscles_router)
app.include_router(exercises_router)
app.include_router(splits_router)

@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

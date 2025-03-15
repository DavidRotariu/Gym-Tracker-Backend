from fastapi import FastAPI

from app.api.routers.auth import auth_router
from app.api.routers.muscles import muscles_router
from app.api.routers.exercises import exercises_router
from app.api.routers.splits import splits_router
from app.api.routers.workout_sessions import workout_sessions_router
from app.api.routers.workouts import workouts_router

app = FastAPI()

# ✅ Register Routers
app.include_router(muscles_router)
app.include_router(exercises_router)
app.include_router(splits_router)
app.include_router(workouts_router)
app.include_router(workout_sessions_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

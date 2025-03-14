from fastapi import FastAPI
from app.api.routers.muscles import muscles_router
from app.api.routers.exercises import exercises_router  # ✅ Import Exercise Router

app = FastAPI()

# ✅ Register Routers
app.include_router(muscles_router)
app.include_router(exercises_router)

@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

from fastapi import FastAPI
from app.api.routers.muscles import muscles_router  # ✅ Ensure correct import

app = FastAPI()

app.include_router(muscles_router)  # ✅ Ensure this is included

@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

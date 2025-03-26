from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.routers.auth import auth_router
from app.api.routers.muscles import muscles_router
from app.api.routers.exercises import exercises_router
from app.api.routers.splits import splits_router
from app.api.routers.users import qrcode_router
from app.api.routers.workout_sessions import workout_sessions_router
from app.api.routers.workouts import workouts_router
from app.api.routers.favourites import favorites_router

app = FastAPI()


# Allow CORS for all origins, methods, and headers (Change for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.11:3000",
                   "http://localhost:3001", "http://192.168.1.11:3001",
                   "http://localhost:3002", "http://192.168.1.11:3002",
                   "http://localhost:3003", "http://192.168.1.11:3003",
                   "http://localhost:3004", "http://192.168.1.11:3004",
                   "http://10.11.8.231:3000"
                   "http://10.11.8.231:3001",
                   "https://gym-tracker-hempvie8u-davidrotarius-projects.vercel.app",
                   "https://gym-tracker-topaz.vercel.app"],  # Allow only your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Serve uploaded images as static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Register Routers
app.include_router(muscles_router)
app.include_router(exercises_router)
app.include_router(splits_router)
app.include_router(workouts_router)
app.include_router(workout_sessions_router)
app.include_router(auth_router)
app.include_router(qrcode_router)
app.include_router(favorites_router)

@app.get("/")
def health_check():
    return {"status": "ok"}

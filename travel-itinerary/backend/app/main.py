from fastapi import FastAPI
from api.routes import router as itinerary_router
from fastapi.middleware.cors import CORSMiddleware
from db.mongo import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown  
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)


# CORS (for React to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from the itinerary module
app.include_router(itinerary_router)

@app.get("/")
def root():
    return {"message": "Itinerary API is running"}
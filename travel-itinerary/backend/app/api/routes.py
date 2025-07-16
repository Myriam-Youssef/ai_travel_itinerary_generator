from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
from models.models import ItineraryInput, Itinerary, ItineraryAdjustment
from services.itinerary_service import generate_itinerary, get_itinerary, save_itinerary, get_all_itineraries, adjust_itinerary, delete_itinerary


router = APIRouter()

@router.post("/api/itinerary/generate", response_model=Itinerary)
async def generate_itinerary_route(itinerary_input: ItineraryInput):
    return await generate_itinerary(itinerary_input)


@router.get("/api/itinerary", response_model=List[Itinerary])
async def get_all_itineraries_route():
    try:
        return await get_all_itineraries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving itineraries: {str(e)}")



@router.get("/api/itinerary/{itinerary_id}", response_model=Itinerary)
async def get_itinerary_route(itinerary_id: str):
    try:
        return await get_itinerary(itinerary_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/itinerary", response_model=Itinerary)
async def save_itinerary_route(itinerary: Itinerary):
    return await save_itinerary(itinerary)


@router.delete("/api/itinerary/{itinerary_id}")
async def delete_itinerary_route(itinerary_id: str):
    try:
        success = await delete_itinerary(itinerary_id)
        if success:
            return {"message": "Itinerary deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Itinerary not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting itinerary: {str(e)}")


@router.patch("/api/itinerary/{itinerary_id}", response_model=Itinerary)
async def adjust_itinerary_route(itinerary_id: str, adjustment: ItineraryAdjustment):
    try:
        return await adjust_itinerary(itinerary_id, adjustment)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ItineraryInput(BaseModel):
    destination: str
    start_date: date
    end_date: date
    interests: List[str]

class DayPlan(BaseModel):
    day: int
    activities: List[str]

class Itinerary(BaseModel):
    id: Optional[str] = None
    destination: str
    start_date: date
    end_date: date
    interests: List[str]
    itinerary: List[DayPlan]

class ItineraryAdjustment(BaseModel):
    adjustment_prompt: str
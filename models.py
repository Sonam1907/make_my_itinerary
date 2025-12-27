from pydantic import BaseModel, Field
from typing import List


class DayPlan(BaseModel):
    day: int = Field(..., description="Day number of the trip")
    city: str = Field(..., description="City for the day")             #I want to change this line
    morning: List[str] = Field(..., description="Morning activities")  # add distance between these activities locations
    afternoon: List[str] = Field(..., description="Afternoon activities")
    evening: List[str] = Field(..., description="Evening activities")
    stay: str = Field(..., description="Hotel or area to stay")        #we can provide stay then each location should have distance from stay
    notes: str = Field(..., description="Important notes or tips")     #if any event is there near the location we can provide that info here base on start_date and end_date


class TripItinerary(BaseModel):
    destination: str = Field(..., description="Main destination")
    total_days: int = Field(..., description="Total number of days")
    start_date: str = Field(..., description="Trip start date")
    end_date: str = Field(..., description="Trip end date")
    budget_level: str = Field(..., description="budget / mid / luxury")
    interests: List[str] = Field(..., description="User interests")
    days: List[DayPlan] = Field(..., description="Day-wise plan")


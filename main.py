from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

# --------------------
# ENUM
# --------------------
class Status(str, Enum):
    active = "active"
    repair = "repair"
    ordered = "ordered"


# --------------------
# MODEL
# --------------------
class Car(BaseModel):
    id: int
    brand: str
    model: str
    year: int = Field(..., ge=1886)
    mileage: float = Field(..., ge=0)
    status: Status
    fuel_consumption: float = Field(..., gt=0)


# --------------------
# "DATABASE" (IN MEMORY)
# --------------------
cars = []


# --------------------
# CREATE CAR
# --------------------
@app.post("/cars", status_code=201)
def add_car(car: Car):
    current_year = 2026

    if car.year > current_year:
        raise HTTPException(status_code=400, detail="Year cannot be in future")

    # защита от дубликатов id
    for c in cars:
        if c.id == car.id:
            raise HTTPException(status_code=400, detail="Car already exists")

    cars.append(car)
    return car


# --------------------
# GET ALL CARS (filter + pagination)
# --------------------
@app.get("/cars")
def get_cars(
    status: Status | None = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    result = cars

    if status:
        result = [c for c in result if c.status == status]

    return result[offset:offset + limit]


# --------------------
# GET BY ID
# --------------------
@app.get("/cars/{car_id}")
def get_car(car_id: int):
    for car in cars:
        if car.id == car_id:
            return car

    raise HTTPException(status_code=404, detail="Car not found")


# --------------------
# UPDATE CAR
# --------------------
@app.put("/cars/{car_id}")
def update_car(car_id: int, updated: Car):
    for i, car in enumerate(cars):
        if car.id == car_id:
            cars[i] = updated
            return updated

    raise HTTPException(status_code=404, detail="Car not found")


# --------------------
# DELETE CAR
# --------------------
@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    for i, car in enumerate(cars):
        if car.id == car_id:
            cars.pop(i)
            return

    raise HTTPException(status_code=404, detail="Car not found")


# --------------------
# TRIP COST CALCULATION
# --------------------
@app.get("/cars/{car_id}/trip-cost")
def trip_cost(
    car_id: int,
    distance: float = Query(..., gt=0),
    fuel_price: float = Query(..., gt=0)
):
    for car in cars:
        if car.id == car_id:

            fuel_needed = (car.fuel_consumption / 100) * distance
            total_cost = fuel_needed * fuel_price

            return {
                "car_id": car_id,
                "distance_km": distance,
                "fuel_needed_liters": fuel_needed,
                "total_cost": total_cost
            }

    raise HTTPException(status_code=404, detail="Car not found")
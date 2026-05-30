from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from enum import Enum
from datetime import datetime

app = FastAPI()

DATABASE_URL = "sqlite:///cars.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Status(str, Enum):
    active = "active"
    repair = "repair"
    ordered = "ordered"

class CarDB(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Float)
    status = Column(String)
    fuel_consumption = Column(Float)

Base.metadata.create_all(bind=engine)

class Car(BaseModel):
    id: int
    brand: str
    model: str
    year: int = Field(..., ge=1886)
    mileage: float = Field(..., ge=0)
    status: Status
    fuel_consumption: float = Field(..., gt=0)

def get_db():
    return SessionLocal()


@app.post("/cars", status_code=201)
def add_car(car: Car):
    db = get_db()

    if car.year > datetime.now().year:
        raise HTTPException(400, "Year from future")

    if db.query(CarDB).filter(CarDB.id == car.id).first():
        raise HTTPException(400, "Car exists")

    new_car = CarDB(**car.model_dump(), status=car.status.value)

    db.add(new_car)
    db.commit()
    db.close()

    return car


@app.get("/cars")
def get_cars(
    status: Status | None = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    db = get_db()
    query = db.query(CarDB)

    if status:
        query = query.filter(CarDB.status == status.value)

    result = query.offset(offset).limit(limit).all()
    db.close()

    return result


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    db = get_db()

    car = db.query(CarDB).filter(CarDB.id == car_id).first()
    db.close()

    if not car:
        raise HTTPException(404, "Car not found")

    return car


@app.put("/cars/{car_id}")
def update_car(car_id: int, updated: Car):
    db = get_db()

    car = db.query(CarDB).filter(CarDB.id == car_id).first()

    if not car:
        db.close()
        raise HTTPException(404, "Car not found")

    car.mileage = updated.mileage
    car.status = updated.status.value

    db.commit()
    db.close()

    return car


@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    db = get_db()

    car = db.query(CarDB).filter(CarDB.id == car_id).first()

    if not car:
        db.close()
        raise HTTPException(404, "Car not found")

    db.delete(car)
    db.commit()
    db.close()


@app.get("/cars/{car_id}/trip-cost")
def trip_cost(car_id: int, distance: float = Query(...), fuel_price: float = Query(...)):
    db = get_db()

    car = db.query(CarDB).filter(CarDB.id == car_id).first()
    db.close()

    if not car:
        raise HTTPException(404, "Car not found")

    fuel_needed = (car.fuel_consumption / 100) * distance
    total_cost = fuel_needed * fuel_price

    return {
        "car_id": car.id,
        "distance_km": distance,
        "fuel_needed_liters": fuel_needed,
        "total_cost": total_cost
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
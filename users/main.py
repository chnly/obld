#!/usr/bin/python3
# -*- coding:utf-8 -*-

from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session

from users import crud, schemas, models
from users.database import engine, Base, SessionLocal
from users.models import User

application = APIRouter()

Base.metadata.create_all(bind=engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users():
    session = SessionLocal()
    return session.query(User).all()


@application.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # TODO mobile re = Query(..., regex="1\d{10}")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already registered")
    return crud.create_user(db=db, user=user)


@application.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@application.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@application.delete('/{user_id}', response_model=schemas.User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@application.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, update_user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=update_user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already exists")
    updated_user = crud.update_user(db, user_id, update_user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@application.post("/{user_id}/cars/", response_model=schemas.Car)
def create_car_for_user(user_id: int, car: schemas.CarCreate, db: Session = Depends(get_db)):
    if not db.query(models.User).filter(models.User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(models.Car).filter(models.Car.car_id == car.car_id).first():
        raise HTTPException(status_code=404, detail="car_id already exists")
    if db.query(models.Car).filter(models.Car.vin_number == car.vin_number).first():
        raise HTTPException(status_code=404, detail="vin_number already exists")
    return crud.create_user_car(db=db, car=car, user_id=user_id)


@application.get("/cars/", response_model=List[schemas.Car])
async def read_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cars = crud.get_car(db, skip=skip, limit=limit)
    return cars


@application.put("/cars/{car_id}", response_model=schemas.Car)
async def update_car(car_id: int, update_car: schemas.CarUpdate, db: Session = Depends(get_db)):
    if db.query(models.Car).filter(models.Car.car_id == update_car.car_id).first():
        raise HTTPException(status_code=404, detail="car_id already exists")
    if db.query(models.Car).filter(models.Car.vin_number == update_car.vin_number).first():
        raise HTTPException(status_code=404, detail="vin_number already exists")
    updated_car = crud.update_car(db, car_id, update_car)
    if updated_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return updated_car


@application.delete('/cars/{car_id}', response_model=schemas.Car)
async def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = crud.delete_car(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

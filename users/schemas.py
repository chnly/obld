#!/usr/bin/python3
# -*- coding:utf-8 -*-

from typing import List
from fastapi import Query
from pydantic import BaseModel


class CarBase(BaseModel):
    car_id: str
    vin_number: str


class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    pass


class Car(CarBase):
    id: int
    car_id: str
    vin_number: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    mobile: int


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    cars: List[Car] = []

    class Config:
        orm_mode = True

#!/usr/bin/python3
# -*- coding:utf-8 -*-

from sqlalchemy.orm import Session

from users import models, schemas
from users.utils import pwd_context


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, mobile=user.mobile, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, update_user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_dict = update_user.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_user, k, v)
        db.commit()
        db.flush()
        db.refresh(db_user)
        return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        db.flush()
        return db_user


def get_car(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Car).offset(skip).limit(limit).all()


def create_user_car(db: Session, car: schemas.Car1Create, user_id: int):
    db_car = models.Car(**car.dict(), owner_id=user_id)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def relate_user_car(db: Session, user_id: int, car_id: int):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if db_car:
        db_car.owner_id = user_id
        db.commit()
        db.flush()
        return db.query(models.User).filter(models.User.id == user_id).first()


def update_car(db: Session, car_id: int, update_item: schemas.CarUpdate):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if db_car:
        update_dict = update_item.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_car, k, v)
        db.commit()
        db.flush()
        db.refresh(db_car)
        return db_car


def delete_car(db: Session, car_id: int):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if db_car:
        db.delete(db_car)
        db.commit()
        db.flush()
        return db_car

#!/usr/bin/python3
# -*- coding:utf-8 -*-

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(25), unique=True, index=True)
    mobile = Column(Integer, index=True)
    hashed_password = Column(String)
    cars = relationship('Car', back_populates='owner')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    car_id = Column(String, unique=True, nullable=False, comment='车辆ID')
    vin_number = Column(String, unique=True, nullable=False, comment='车辆VIN码')
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='cars')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

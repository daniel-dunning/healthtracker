from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base
from pydantic import BaseModel



class Measurements(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)
    time = Column(String, unique=True, index=True)
    weight = Column(Integer)
    glucose = Column(Integer)
    long_acting_insulin = Column(Integer)
    short_acting_insulin = Column(Integer)
    systolic = Column(Integer)
    diastolic = Column(Integer)
    pulse = Column(Integer)
    fluid_intake = Column(Integer)
    urine_output = Column(Integer)



class MeasurementBase(BaseModel):
    title: str
    description: str | None = None


class MeasurementCreate(MeasurementBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True

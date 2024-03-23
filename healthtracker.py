from datetime import datetime

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dateutil import parser
from starlette import status
from tabulate import tabulate
import json
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import pymysql

DBMS = 'MYSQL'

with open("healthtracker.json", "r") as f:
    data = json.load(f)
print(data)

DB_URL = ""
for item in data:
    if item['DB'] == DBMS:
        DB_URL = item['DB_URL']
        break

print(DB_URL)

engine = create_engine('mysql+pymysql://root:health-metrics@35.199.22.212/health-metrics')

# engine = create_engine(DB_URL)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define SQLAlchemy Model
# SQLAlchemy Model
class Measurement(Base):

    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=True)
    glucose = Column(Float, nullable=True)
    long_acting_insulin = Column(Float, nullable=True)
    short_acting_insulin = Column(Float, nullable=True)
    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)
    pulse = Column(Integer, nullable=True)
    fluid_intake = Column(Integer, nullable=True)
    time = Column(DateTime, default=datetime.utcnow)

# Pydantic Model for Validation
class MeasurementBase(BaseModel):
    weight: float = 0.0
    glucose: float = 0
    long_acting_insulin: float = 0.0
    short_acting_insulin: float = 0.0
    systolic: int = 0
    diastolic: int = 0
    pulse: int = 0
    fluid_intake: int = 0
    time: datetime

    class Config:
        from_attributes = True

Base.metadata.create_all(engine)


class HealthTracker:
    def add_measurement(self, db_session, measurement: MeasurementBase):
        db_measurement = Measurement(**measurement.dict())
        db_session.add(db_measurement)
        db_session.commit()
        return db_measurement

    def get_measurements(self, db_session):
        return db_session.query(Measurement).all()

# Usage
tracker = HealthTracker()
db_session = SessionLocal()
# measurement_data = {
#     "weight": 70.5,
#     "glucose": 5.7,
#     "long_acting_insulin": 20,
#     "short_acting_insulin": 10,
#     "systolic": 120,
#     "diastolic": 80,
#     "pulse": 75,
#     "fluid_intake": 500,
#     "time": datetime.utcnow()
# }
# measurement = MeasurementBase(**measurement_data)
# result = tracker.add_measurement(db_session, measurement)
# print(result.id)
measurements = tracker.get_measurements(db_session)
print(measurements)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    all_measurements = tracker.get_measurements(db_session)
    return templates.TemplateResponse("index.html", {"request": request, "measurements": all_measurements})


@app.post("/add_measurement/")
async def add_measurement(request: Request,
                          weight: float = Form(0),
                          glucose: float = Form(0),
                          long_acting_insulin: float = Form(0),
                          short_acting_insulin: float = Form(0),
                          systolic: int = Form(0),
                          diastolic: int = Form(0),
                          pulse: int = Form(0),
                          fluid_intake: int = Form(0),
                          from_form: str = Form(1),
                          time: str = Form(...)):
    measurement_time = parser.parse(time)
    measurement_data =  {
        "weight": weight,
        "glucose": glucose,
        "long_acting_insulin": long_acting_insulin,
        "short_acting_insulin": short_acting_insulin,
        "systolic": systolic,
        "diastolic": diastolic,
        "pulse": pulse,
        "fluid_intake": fluid_intake,
        "time": measurement_time
    }
    new_measurement = MeasurementBase(**measurement_data)

    tracker.add_measurement(db_session, new_measurement)

    # tracker.add_measurement(weight, glucose, long_acting_insulin, short_acting_insulin, systolic, diastolic, pulse, fluid_intake, measurement_time)
    if from_form == '1':
        redirect_url = request.url_for('home')
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    else:
        return {"message": "Measurement added successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

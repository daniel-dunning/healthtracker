from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class HealthTracker:
    def __init__(self):
        self.measurements = []

    def add_measurement(self, weight=None, glucose=None, long_acting_insulin=None, short_acting_insulin=None, systolic=None, diastolic=None, time=None):
        measurement = {
            "weight": weight,
            "glucose": glucose,
            "long_acting_insulin": long_acting_insulin,
            "short_acting_insulin": short_acting_insulin,
            "systolic": systolic,
            "diastolic": diastolic,
            "time": time.strftime("%Y-%m-%d %H:%M:%S") if time else None
        }
        self.measurements.append(measurement)
        if time:
            self.save_to_file(measurement)

    def save_to_file(self, measurement):
        with open("measurements.json", "a") as file:
            json.dump(measurement, file)
            file.write("\n")

    def get_measurements(self):
        return self.measurements


tracker = HealthTracker()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    measurements = tracker.get_measurements()
    return templates.TemplateResponse("index.html", {"request": request, "measurements": measurements})

@app.post("/add_measurement/")
async def add_measurement(request: Request,
                          weight: float = Form(None),
                          glucose: float = Form(None),
                          long_acting_insulin: float = Form(None),
                          short_acting_insulin: float = Form(None),
                          systolic: int = Form(None),
                          diastolic: int = Form(None),
                          time: str = Form(...)):
    measurement_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S") if time else None
    tracker.add_measurement(weight, glucose, long_acting_insulin, short_acting_insulin, systolic, diastolic, measurement_time)
    return {"message": "Measurement added successfully."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

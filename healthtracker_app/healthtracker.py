from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from dateutil import parser
from starlette import status
from tabulate import tabulate
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class HealthTracker:
    m_keys = ["time","weight","glucose","long_acting_insulin","short_acting_insulin","systolic","diastolic","pulse",
              "fluid_intake"]

    def __init__(self):
        self.measurements = []

    def add_measurement(self, weight="", glucose=None, long_acting_insulin=None, short_acting_insulin=None, systolic=None, diastolic=None, pulse="", fluid_intake=None, time=None):
        measurement = {
            "weight": weight,
            "glucose": glucose,
            "long_acting_insulin": long_acting_insulin,
            "short_acting_insulin": short_acting_insulin,
            "systolic": systolic,
            "diastolic": diastolic,
            "pulse": pulse,
            "fluid_intake": fluid_intake,
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
        new_measurements = []
        def replace_none_with_empty_str(some_dict):
            return {k: ('' if v is None else v) for k, v in some_dict.items()}

        # replace None with blanks for formatting
        for measurement in self.measurements:
            m = replace_none_with_empty_str(measurement)
            new_measurements.append(m)

        # sort measurements
        new_measurements = sorted(new_measurements, key=lambda x: x['time'])

        return new_measurements



    def load_from_file(self):
        with open("measurements.json", "r") as file:
            for line in file:
                measurement = json.loads(line.strip())
                self.measurements.append(measurement)

tracker = HealthTracker()
tracker.load_from_file()  # Load measurements from file at startup


# program to convert json measurements into a tabulate

def convert_measurements_to_list(measurements:list=None):
    end_result = []
    for measurement in reversed(measurements):
        result = []
        for key in tracker.m_keys:
            result.append(measurement.get(key, ""))
        end_result.append(result)

    return end_result

# html table for measurements
def list_to_html_table(measurements:list=None):

    # construct the table
    table = ["<table id='measurements'>"]
    # set the header row
    header = ""
    for key in tracker.m_keys:
        header += f"<th>{key}</th>"
    table.append(f"<tr>{header}</tr>")


    for measurement in measurements:
        row = ""
        for cell in measurement:
            row += f"<td>{cell}</td>"
        table.append(f"<tr>{row}</tr>")
    table.append("</table>")
    return table

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    measurements = tracker.get_measurements()
    m2 = convert_measurements_to_list(measurements)
    m2 = tabulate(m2,headers=tracker.m_keys,tablefmt="grid")
    print(m2)
    # Html_file = open("measurement.html", "w")
    # Html_file.write(measurements)
    # Html_file.close()

    #table = list_to_html_table(measurements)
    return templates.TemplateResponse("index.html", {"request": request, "measurements": measurements})

@app.post("/add_measurement/")
async def add_measurement(request: Request,
                          weight: float = Form(None),
                          glucose: float = Form(None),
                          long_acting_insulin: float = Form(None),
                          short_acting_insulin: float = Form(None),
                          systolic: int = Form(None),
                          diastolic: int = Form(None),
                          pulse: int = Form(None),
                          fluid_intake: int = Form(None),
                          from_form: str = Form(None),
                          time: str = Form(...)):
    measurement_time = parser.parse(time)                          
    # measurement_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S") if time else None
    tracker.add_measurement(weight, glucose, long_acting_insulin, short_acting_insulin, systolic, diastolic, pulse, fluid_intake, measurement_time)
    if from_form == '1':
        redirect_url = request.url_for('home')
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    else:
        return {"message": "Measurement added successfully."}

@app.get("/measurements/")
async def get_all_measurements():
    measurements = tracker.get_measurements()
    return JSONResponse(content=measurements)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

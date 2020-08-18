from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func, inspect, distinct
from datetime import datetime as dt
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
app = Flask(__name__)

@app.route("/")
def home():
#     List all available api routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_end")

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precipitation = []
    for result in results:
        result_dict = {}
        result_dict[result[0]] = result[1]
        precipitation.append(result)

    return jsonify(precipitation)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name)
    session.close()

    station_list = []
    for station in stations:
        dict = {"Station ID:":stations[0], "Station Name": stations[1]}
        station_list.append(dict)
    return jsonify(station_list)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs(): 
    Last_Date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close()
    last_date = Last_Date[0]
    year_ago = dt.date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:11])) - dt.timedelta(days = 365)
    tobs_results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago,\
        Measurement.station == most_active).all()
    return jsonify(tobs_results)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.   

@app.route("/api/v1.0/<start>")
def temp_start(start):

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    session.close()
    temps = list(np.ravel(results)) 

    return jsonify(temps = temps)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    session.close()
    temps = list(np.ravel(results)) 

    return jsonify(temps = temps)

if __name__ == '__main__':
    app.run(debug=True)

    
# i need to import which i import at climate_analysis part
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib import style
style.use('seaborn')

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# available routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    last_date = (session
            .query(Measurement.date)
            .order_by(Measurement.date.desc()).first())

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results_of_last_year = (session
                       .query(Measurement.date, Measurement.prcp)
                       .filter(Measurement.date > year_ago)
                       .order_by(Measurement.date).all())
                       
    # first i need a list od dictionary.
    rain_records = []

    for record in results_of_last_year:
        
        row = {}


        row['Date'] = record[0]
        row['tobs'] = record[1]

        rain_records.append(row)

    return jsonify(rain_records)



@app.route("/api/v1.0/stations")
def stations():
    busy_station = (session
                .query(Measurement.station)
                .group_by(Measurement.station)
                .order_by(func.count(Measurement.tobs).desc()).all()
               )


    return jsonify(busy_station)


@app.route("/api/v1.0/tobs")
def tobss():

    year_ago = dt.date.today() - dt.timedelta(days=365)

    temp_obs = (session
            .query(Measurement.station, Measurement.date, Measurement.tobs)
            .filter(Measurement.date > year_ago)
            .order_by(Measurement.date).all())

    temp_record = []

    for row in temp_obs:

        record = {}

        record['station'] = row[0]
        record['date'] = row[1]
        record['temperature']  = row[2]

        temp_record.append(record)


    return jsonify(temp_record)

@app.route("/api/v1.0/date")
def temps():

    trip_start = dt.date(2018, 8, 2)
    trip_end = dt.date(2018, 8, 9)
    one_year = dt.timedelta(days=365)
    start_date = trip_start - one_year
    end_date = trip_end - one_year
    
    temp_cals = (session
            .query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
           .filter(Measurement.date >= start_date)
           .filter(Measurement.date <= end_date)
           .all()
           )
    record_temp = []

    for row in temp_cals:
        record = {}

        record['TMIN'] = row[0]
        record['TAVG'] = row[1]
        record['TMAX'] = row[2]
        record_temp.append(record)



    return jsonify(record_temp)

if __name__ == '__main__':
    app.run(debug=True)

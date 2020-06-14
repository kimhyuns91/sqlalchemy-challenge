import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    print("Server received request for 'Home' page....")
    return(
        f"SQLAlchemy Challenge. <br/>"
        f"Available Routes: <br/><br/>"

        f"/api/v1.0/precipitation<br/>"
        f"Dates and precipitation from the last year in data set. <br/><br/>"

        f"/api/v1.0/stations<br/>"
        f"List of stations. <br/><br/>"

        f"/api/v1.0/tobs<br/>"
        f" List of temperature observations of the most active station for its last year in data set. <br/><br/>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Min, max, and average temperatures from given start date to end of the date in the data.<br/><br/>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"Min, max, and average temperatures for a given range of the time."
   ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).first()
    str_last_date = ''.join(last_date)
    last_date2 = str_last_date.split('-')
    
    #Date 1 year ago
    query_date= dt.date(int(last_date2[0]),int(last_date2[1]),int(last_date2[2]))-dt.timedelta(days=365)

    #Last date in the databse
    limit_date = dt.date(int(last_date2[0]),int(last_date2[1]),int(last_date2[2]))

    #Capture date and precipitation data
    precipt = session.query(Measurement.station, Measurement.date, Measurement.prcp).\
    filter(Measurement.date > query_date).\
    filter(Measurement.date <= limit_date).all()
    
    # Create a dictionary from the row data and append to a list of all_passengers
    prcp_list = []
    for station, date, prcp in precipt:
        data_dict = {}
        data_dict["station"] = station
        data_dict["date"] = date
        data_dict["precipitation"] = prcp
        prcp_list.append(data_dict)


    session.close()

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stns = session.query(Station.name).all()
    session.close()
    return jsonify(stns)
      
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Choose the station with the highest number of temperature observations.
    temp_station = session.query(Measurement.station, func.count(Measurement.tobs)).\
    group_by(Measurement.station).first()

    top_count_temp_station=temp_station[0]
    
    #Capture the last date and date of one year prior for the captured station
    temp_last_date = session.query(func.max(Measurement.date)).\
        filter(Measurement.station == top_count_temp_station).first()

    temp_str_last_date = ''.join(temp_last_date)
    temp_last_date2 = temp_str_last_date.split('-')

    #One year prior
    temp_query_date= dt.date(int(temp_last_date2[0]),int(temp_last_date2[1]),int(temp_last_date2[2]))-dt.timedelta(days=365)

    #Last date
    temp_limit_date = dt.date(int(temp_last_date2[0]),int(temp_last_date2[1]),int(temp_last_date2[2]))
    
    #Capture the date and the temperature
    tobs_query = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == top_count_temp_station).\
    filter(Measurement.date > temp_query_date).\
    filter(Measurement.date <= temp_limit_date).\
    all()
    
    tobs_list = []
    for station, date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["Station"] = station
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_list.append(tobs_dict)
    
    session.close()
    
    return jsonify(tobs_list)
    
@app.route('/api/v1.0/<date>/')
def start_date(date):
    session = Session(engine)
    Tdate = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= date).all()

    temp1_list = []
    for min1, max1, average1 in Tdate:
        temp1_dict = {}
        temp1_dict['Start_Date'] = date
        temp1_dict['Tmin'] = min1
        temp1_dict['Tmax'] = max1
        temp1_dict['Tavg'] = average1
        temp1_list.append(temp1_dict)

    session.close()

    return jsonify(temp1_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def rage_dates(start_date, end_date):
    session = Session(engine)
    range_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    range_list = []
    for min2, max2, average2 in range_temp:
        temp2_dict = {}
        temp2_dict['Start Date'] = start_date
        temp2_dict['End Date'] = end_date
        temp2_dict['Tmin'] = min2
        temp2_dict['Tmax'] = max2
        temp2_dict['Tavg'] = average2
        range_list.append(temp2_dict)
    
    session.close()
    
    return jsonify(range_list)
    
if __name__ == "__main__":
    app.run(debug=True)
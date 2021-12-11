#Dependencies
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement


session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#homepage and list routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
    f"Available Routes:<br/><br/>"
    f"<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"<br/>"
    f"/api/v1.0/stations<br/>"
    f"<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"/api/v1.0/start<br/>"
    f"<br/>"
    f"/api/v1.0/start/end<br/>"
    )
    
#precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.station,Measurement.date,Measurement.prcp).filter(Measurement.date>year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to precipitation data
    all_prcp = []
    for station, date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_dict["Station"] = station
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


# stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return JSON list of stations"""
    # Query stations
    station_results = session.query(Measurement.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list for all stations
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

# tobs
@app.route("/api/v1.0/tobs")
def TOBS():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    """Return JSON list TOBS for previous year"""
    # Query dates and temp obs for most active station
    temps = session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>year_ago).filter(Measurement.station=='USC00519281').all()

    session.close()
    # Create a dictionary from the row data and append to temp data
    all_temps = []
    for station, date, tobs in temps:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["TOBS"] = tobs
        temp_dict["Station"] = station
        all_temps.append(temp_dict)

    return jsonify(all_temps)


#start date
@app. route("/api/v1.0/<start>")
    ##calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
def start_stats(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query temp data for min, max and avg for start date
    start_stats = session.query(Measurement.station,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>=start).all()   
    session.close()
    
    return jsonify(temps = list(np.ravel(start_stats)))

#start_end date
@app. route("/api/v1.0/<start>/<end>")
    ##calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def end_stats(start, end):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query temp data for min, max and avg for start date to end date
    end_stats = session.query(Measurement.station,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()     
    session.close()
    
     # Create a dictionary for temp data for min, max and avg for start date to end date
    temp_dict = []
    for station, min_tobs, max_tobs, avg_tobs in end_stats:
        sum_dict = {}
        sum_dict["Max Temp"] = max_tobs
        sum_dict["Min Temp"] = min_tobs
        sum_dict["Avg Temp"] = avg_tobs
        temp_dict.append(sum_dict)

    return jsonify(temp_dict)

#session.close()

if __name__ == "__main__":
    app.run(debug=True)
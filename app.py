import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import Column, Integer, String, Float

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"<h1><p style=\"text-align:center;\">Surfs Up</p></h1>"
        f"Please select a link to continue and close the new tab after you're done:<br/>"
        f"<p>"
        f"<a href=\"http://127.0.0.1:5000/api/v1.0/precipitation\" target=\"_blank\">/api/v1.0/precipitation</a>"
        f"<p>"
        f"<a href=\"http://127.0.0.1:5000/api/v1.0/stations\" target=\"_blank\">/api/v1.0/stations</a>"
        f"<p>"
        f"<a href=\"http://127.0.0.1:5000/api/v1.0/tobs\" target=\"_blank\">/api/v1.0/tobs</a>"
        f"<p>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"<font color=red>** Replace YYYY-MM-DD with Start Date when pasting the string after 127.0.0.1:5000</font><br/>"
        f"<p>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"   
        f"<font color=red>** Replace the first YYYY-MM-DD for Start Date and second YYYY-MM-DD for End Date when pasting the string after 127.0.0.1:5000</font><br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Get the latest date
    MaxDate = engine.execute("SELECT MAX(date) FROM Measurement").fetchall()
    EndDate = MaxDate[0][0]

    Year = int(EndDate[0:4])
    Month = int(EndDate[5:7])
    Day = int(EndDate[8:])

    StartDate = dt.date(Year, Month, Day) - dt.timedelta(days=365)

    # Retrieve the last 12 months of precipitation data
    prcp_data = session.query(Measurement.date,Measurement.prcp)\
                          .filter(Measurement.date <= EndDate)\
                          .filter(Measurement.date >= StartDate)\
                          .order_by(Measurement.date.desc()).all()
    list = []
    for result in prcp_data:
        dict = {"Date":result[0],"Precipitation":result[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    # List the stations.
    Stations_desc = session.query(Station.station,Station.name)\
                                     .order_by(Station.name.desc()).all()
    
    list=[]
    for station in Stations_desc:
        dict = {"Station ID:":station[0],"Station Name":station[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
     # Get the latest date
    MaxDate = engine.execute("SELECT MAX(date) FROM Measurement").fetchall()
    EndDate = MaxDate[0][0]

    Year = int(EndDate[0:4])
    Month = int(EndDate[5:7])
    Day = int(EndDate[8:])

    StartDate = dt.date(Year, Month, Day) - dt.timedelta(days=365)
    
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    tobs_temp = session.query(Measurement.date,Measurement.tobs)\
             .filter(Measurement.date >= StartDate).filter(Measurement.date<=EndDate)\
             .order_by(Measurement.date.desc()).all()

    list = []
    for temp in tobs_temp:
        dict = {"Date": temp[0], "Temperture": temp[1]}
        list.append(dict)

    return jsonify(list)  

@app.route("/api/v1.0/<start>")
def startdate(start):
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    #list = []
    print(f"Temperature Analysis for the dates greater than or equal to the start date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
        
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def startenddate(start,end):         
    """ When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive. """    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    print(f"Temperature Analysis for dates between the start and end date inclusive.")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)    

if __name__ == '__main__':
    app.run(debug=True)
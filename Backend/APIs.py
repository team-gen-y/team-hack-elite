from flask import Flask, jsonify, request, json
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)
import MySQLdb
import math
import json
import pandas as pd
import numpy as np
import datetime
import warnings
from datetime import timedelta
import pickle as p
from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import autocorrelation_plot

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'solrock'
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_DB'] = 'information' 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'secret'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


CORS(app)

warnings.filterwarnings('ignore')
raw_data = pd.read_csv('covid_19_india.csv')

x = np.array(raw_data['Time'])
u = np.unique(x)
                                                                    # replacing the AM-PM timestyle with 24 hour timestyle
raw_data['Time'][raw_data['Time'] == '10:00 AM'] = '10:00:00' 
raw_data['Time'][raw_data['Time'] == '10:00 AM'] = '10:00:00' 
raw_data['Time'][raw_data['Time'] == '8:00 AM'] = '08:00:00'
raw_data['Time'][raw_data['Time'] == '5:00 PM'] = '17:00:00'                                     # replacing the AM-PM timestyle with 24 hour timestyle
raw_data['Time'][raw_data['Time'] == '6:00 PM'] = '18:00:00'
raw_data['Time'][raw_data['Time'] == '7:30 PM'] = '19:30:00'
raw_data['Time'][raw_data['Time'] == '8:30 PM'] = '20:30:00'
raw_data['Time'][raw_data['Time'] == '9:30 PM'] = '21:30:00'    

raw_data['Date'] = raw_data['Date'] + '20'
raw_data['Datetime'] = raw_data['Date'] + ' ' + raw_data['Time']
for i in range(len(raw_data['Datetime'])):
  raw_data['Datetime'][i] = datetime.datetime.strptime(raw_data['Datetime'][i],'%d/%m/%Y %H:%M:%S')  

statewise = raw_data.groupby('State/UnionTerritory')['Confirmed','Deaths','Cured'].max()
statewise['Active'] = statewise['Confirmed'] - statewise['Deaths'] - statewise['Cured']



@app.route('/register', methods=['POST'])
def register():                                 #register route
    cur = mysql.connection.cursor()
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
	
    cur.execute("CREATE TABLE IF NOT EXISTS  user (first_name varchar(50), last_name varchar(50), email varchar(100), password varchar(100));")
    cur.execute("INSERT INTO user (first_name, last_name, email, password) VALUES ('" + 
		str(first_name) + "', '" + 
		str(last_name) + "', '" + 
		str(email) + "', '" + 
		str(password) + "')")
    mysql.connection.commit()
	

    return "success"



@app.route('/login', methods=['POST'])
def login():                            #login route
    cur = mysql.connection.cursor()
    email = request.get_json()['email']
    password = request.get_json()['password']
    result = ""
	
    cur.execute("SELECT * FROM user where email = '" + str(email) + "'")
    rv = cur.fetchone()
	
    if bcrypt.check_password_hash(rv['password'], password):
        access_token = create_access_token(identity = {'first_name': rv['first_name'],'last_name': rv['last_name'],'email': rv['email']})
        result = access_token
    else:
        result = jsonify({"error":"Invalid username and password"})
    
    return result




@app.route('/country', methods=['POST'])
def predcountry():
    days_in_advance = request.get_json()['days_in_advance']

    def country(raw_data,days_in_adv):
        raw_data['Datetime'] = raw_data['Date'] + ' ' + raw_data['Time']
        for i in range(len(raw_data['Datetime'])):
            raw_data['Datetime'][i] = datetime.datetime.strptime(raw_data['Datetime'][i],'%d/%m/%Y %H:%M:%S')  
             #print(raw_data['Datetime'])     
        country_data = raw_data.groupby("Datetime")[["Confirmed","Cured","Deaths"]].sum().reset_index()
        country_data['Active'] = country_data['Confirmed'] - country_data['Cured'] - country_data['Deaths']            #print(country_data)                             
        country_data['ds'] = country_data['Datetime']
        country_data['y'] = country_data['Confirmed'] 
        testing = country_data.loc[:,('Confirmed','Datetime')]
        model2 = ARIMA(testing['Confirmed'],order = [1,1,0])
        model2 = model2.fit(trend = 'c')
        forecast = model2.forecast(steps = 30)
        pred = list(forecast[0])
        return pred[days_in_adv].astype(int)

    val = country(raw_data,days_in_advance)
    return("Expected confirmed cases by " + str((datetime.datetime.today().date()+timedelta(days=2)))+" are " + str(val))




@app.route('/state',methods=['POST'])
def predstate():
    days = request.get_json()['days']
    State = request.get_json()['State']
    
    def pred_state(raw_data,state,days_in_adv):
        delh = raw_data[raw_data['State/UnionTerritory'] == state].reset_index()
        tdata = delh.loc[:,('Datetime','Confirmed')]
        model1 = ARIMA(tdata['Confirmed'],order = [5,1,0])
        model1 = model1.fit(trend = 'c')
        forec = model1.forecast(steps = 30)
        pred = list(forec[0])
        return pred[days_in_adv].astype(int)

    val2 = pred_state(raw_data,State,days)
    return("Expected Confirmed cases in " + State + " by " + str((datetime.datetime.today().date()+timedelta(days=days)))+" is "+str(val2))




@app.route('/application_form',methods=['POST'])
def application_form():

    cur = mysql.connection.cursor()

    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    age = request.get_json()['age']
    destination = request.get_json()['destination']
    aadhar_number = request.get_json()['aadhar_number']

    try:
        cur.execute("CREATE TABLE IF NOT EXISTS  applicants (first_name varchar(50), last_name varchar(50), age integer(10), destination varchar(50), aadhar_number varchar(50));")
        cur.execute("INSERT INTO applicants (first_name, last_name, age, destination, aadhar_number) VALUES ('" + 
            str(first_name) + "', '" + 
            str(last_name) + "', '" + 
            str(age) + "', '" + 
            str(destination) + "','" + 
            str(aadhar_number) + "')")

        mysql.connection.commit()
        return 'success'
    
    except MySQLdb.Error:
        return ("aadhar already registered")

@app.route('/coordinates', methods = ["POST"])
def coordinates():
    x = request.get_json()["x"]
    y = request.get_json()["y"]
    radius = request.get_json()["radius"]

    def return_waypoints(x,y,radius):
        waypoints = np.zeros((6,2))
        waypoints[0] = [x + (radius/math.sqrt(3)), y + radius]
        waypoints[1] = [x + (radius/math.sqrt(3)), y - radius]
        waypoints[2] = [x - (radius/math.sqrt(3)), y + radius]
        waypoints[3] = [x - (radius/math.sqrt(3)), y - radius]
        waypoints[4] = [x - radius, y]
        waypoints[5] = [x + radius, y]
        x = list(waypoints[:,0])
        y = list(waypoints[:,1])
        return (x,y)
    
    return json.dumps(return_waypoints(x,y,radius))        
 
if __name__ == '__main__':
    app.run(debug=True)

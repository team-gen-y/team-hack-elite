from flask import Flask, jsonify, request, json, render_template, send_file
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)
import MySQLdb
import math
import urllib
import sys
import json
import pandas as pd
import numpy as np
import datetime
import warnings
from datetime import timedelta
import pickle as p
from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import autocorrelation_plot
import sys
from datetime import date
import chart_studio.plotly as pl
import plotly.graph_objs as gobj
from selenium import webdriver
import time
import urllib.request
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import folium

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



@app.route('/distwise', methods = ["GET","POST"])
def dist():
    state = request.get_json()["state"]
    district = request.get_json()["district"]

    ur2 = "https://api.covid19india.org/districts_daily.json"
    resp = urllib.request.urlopen(ur2)
    x = json.loads(resp.read())
    k = x['districtsDaily']
    def get_dist_data(state,district):
        at = k[state]
        stats = at[district][-1]
        return stats

    return get_dist_data(state,district)


@app.route("/world")
def world_map():
    return render_template('temp-plot.html')


@app.route("/state_graph_data", methods = ["GET"])
def stategraphdata():
    ur5 = "https://api.covid19india.org/csv/latest/case_time_series.csv	"
    with request.urlopen(ur5) as response:
        x = pd.read_csv(response)

    l = pd.DataFrame()
    for i in range(len(x['Daily Confirmed'])):
        if i%15 == 0:
            l = l.append(x.iloc[i,:])
    l = l.append(x.iloc[-1,:])
    # print(l.columns)
    l['Total Active'] = l['Total Confirmed'] - l['Total Deceased'] - l['Total Recovered']
    fin = l.loc[:,('Date','Total Confirmed','Total Recovered','Total Deceased','Total Active')]
    fin = fin.reset_index(drop = True)
    # print(fin)
    y = pd.DataFrame.to_json(fin)
    jsonfile = json.dumps(y)
    return jsonfile


@app.route("/worldmapstats", methods = ["GET"])
def newworldstats():
    ur1 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    ur2 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    ur3 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    xt1 = pd.read_csv(ur1)
    xt2 = pd.read_csv(ur2)
    xt3 = pd.read_csv(ur3)

    da = (date.today()-timedelta(1)).strftime("%#m/%d/%y")
    conf = pd.Series(xt1.groupby('Country/Region')[str(da)].max())
    dea = xt2.groupby('Country/Region')[str(da)].max()
    rec = xt3.groupby('Country/Region')[str(da)].max()
    #test = pd.DataFrame([xt1['Country/Region'],conf[da]])
    world_data_old = pd.DataFrame([conf,dea,rec])
    world_data_new = world_data_old.T
    world_data_new.columns = ['Confirmed','Deaths','Recovered']
    world_data_new['Active'] = world_data_new['Confirmed'] - world_data_new['Recovered'] - world_data_new['Deaths']
    world_data_new = world_data_new.reset_index()
    world_data_new = world_data_new.set_index('Country/Region')
    #print(world_data_new)
    #world_data = pd.DataFrame([conf,dea,rec])
    #print(world_data)
    fin = pd.DataFrame.to_json(world_data_new)
    fin = json.dumps(fin)
    #print(fin)

    from plotly.offline import download_plotlyjs,init_notebook_mode,plot
    world_plot = world_data_new.reset_index()
    data = dict(type = 'choropleth',
                locations = world_plot['Country/Region'],
                locationmode = 'country names',
                autocolorscale = False,
                colorscale = 'Rainbow',
                text= world_plot['Country/Region'],
                z=world_plot['Deaths'],
                marker = dict(line = dict(color = 'rgb(255,255,255)',width = 1)),
                colorbar = {'title':'Colour Range','len':0.25,'lenmode':'fraction'})
    layout = dict(geo = dict(scope='world'))
    worldmap = gobj.Figure(data = [data],layout = layout)
    return plot(worldmap)



@app.route("/statsheatmaps_Active", methods = ["GET"])
def barandmap_A():

    filename_Active = '/home/ubuntu/Backend/Active.png'
    return send_file(filename_Active, mimetype='image/png')


@app.route("/statsheatmaps_Confirmed", methods = ["GET"])
def barandmap_C():

    filename_Confirmed = '/home/ubuntu/Backend/Confirmed.png'
    return send_file(filename_Confirmed, mimetype='image/png')


@app.route("/statsheatmaps_Recovered", methods = ["GET"])
def barandmap_R():

    filename_Recovered = '/home/ubuntu/Backend/Recovered.png'
    return send_file(filename_Recovered, mimetype='image/png')

@app.route("/statsheatmaps_Deaths", methods = ["GET"])
def barandmap_D():
   
    filename_Deaths = '/home/ubuntu/Backend/Deaths.png'
    return send_file(filename_Deaths, mimetype='image/png')

@app.route("/statsheatmaps_Active_w", methods = ["GET"])
def barandmap_A_w():

    filename_Active = '/home/ubuntu/Backend/Active_world.png'
    return send_file(filename_Active, mimetype='image/png')


@app.route("/statsheatmaps_Confirmed_w", methods = ["GET"])
def barandmap_C_w():

    filename_Confirmed = '/home/ubuntu/Backend//Confirmed_world.png'
    return send_file(filename_Confirmed, mimetype='image/png')


@app.route("/statsheatmaps_Recovered_w", methods = ["GET"])
def barandmap_R_w():

    filename_Recovered = '/home/ubuntu/Backend/Recovered_world.png'
    return send_file(filename_Recovered, mimetype='image/png')

@app.route("/statsheatmaps_Deaths_w", methods = ["GET"])
def barandmap_D_w():
   
    filename_Deaths = '/home/ubuntu/Backend//Deaths_world.png'
    return send_file(filename_Deaths, mimetype='image/png')

@app.route("/statsbarchart")
def chart():
    ur2 = "https://api.covid19india.org/csv/latest/state_wise.csv"
    xt = pd.read_csv(ur2)
    #print(xt.columns)
    fin = xt.groupby('State')['Confirmed','Deaths','Recovered','Active','Last_Updated_Time'].max()
    lk = fin.reset_index()
    #print(fin.iloc[:,:-1])
    line = pd.DataFrame({"State":'Daman and Diu',"Confirmed":lk.loc[7,"Confirmed"],"Deaths":lk.loc[7,"Deaths"],"Recovered":lk.loc[7,"Recovered"],"Active":lk.loc[7,"Active"],"Last_Updated_Time":lk.loc[7,"Last_Updated_Time"]},index = [7.5])
    #print(line)
    lk.loc[7,'State'] = "Dadra and Nagar Haveli"
    #lk.append(line,ignore_index=False)
    #lk = lk.reset_index()
    lk = lk.append(line,ignore_index=False)
    lk = lk.sort_index().reset_index(drop=True)
    lk = lk.drop(31)
    #lk = lk.drop(18)
    lk = lk.drop(34)
    lk['ID_1'] = range(1,len(lk['Confirmed'])+1)
    lk.loc[33,'ID_1'] = 36
    lk.loc[34:38,'ID_1'] = lk.loc[34:38,'ID_1'] - 1
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #print(lk)
    final = lk.set_index('State')
    jd = pd.DataFrame.to_json(final)
    return jd


if __name__ == '__main__':
    app.run()

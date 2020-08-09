from datetime import date
from datetime import timedelta
import urllib
import json
import pandas as pd
import sys
import folium
import webbrowser
import imgkit
from selenium import webdriver
import time
import urllib.request
import os
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options
# from pyvirtualdisplay import Display

ur1 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
ur2 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
ur3 = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
xt1 = pd.read_csv(ur1)
xt2 = pd.read_csv(ur2)
xt3 = pd.read_csv(ur3)
da = (date.today()-timedelta(1)).strftime("%-m/%-d/%-y")
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
world_plot = world_data_new.reset_index()

#print(x)
#from google.colab import files
#files.download('temp-plot.html')
ur4 = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
dat = json.load(urllib.request.urlopen(ur4))

import webbrowser
import folium
world_plot.loc[174,'Country/Region'] = "United States of America"
print(world_plot.loc[178,'Confirmed'])
def auto_open(path):
    html_page = "{}".format(path)
    new = 2
    webbrowser.open(html_page, new=new)
def state_map(params='Confirmed'):
    df = world_plot.loc[:, ('Country/Region', params)]  # Params can be any of Confirmed, Active, Recovered and Deaths
    k = df[params].max()
    print(k)
    if params != 'Active':
        bins = list([0,k*0.02,k*0.05,k*0.1,k*0.2,k*0.4,k*0.6,k*0.7,k*1.5])
    else:
        bins = 6
    colPal = {'Confirmed':'Greens','Recovered':'Blues','Deaths':'Reds','Active':'YlOrBr'}
    world_map = folium.Map(location=[6.465422,3.406448],zoom_start=1,tiles = 'CartoDB positron')
    folium.Choropleth(
        geo_data=dat,
        data=df,
        columns=['Country/Region', params],
        key_on='feature.properties.name',
        fill_color=colPal[params],
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='COVID 19 ' + str(params) + ' Heat Map',
        bins= bins
    ).add_to(world_map)
    x = world_map
    return x


# options = Options()
# options.headless = True
# driver = webdriver.Chrome("/usr/bin/chromedriver",chrome_options = options)
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(600,600))
# display.start()
dats = ['Confirmed','Recovered','Deaths','Active']
for x in dats:
    state_map(x).save(str(x)+'_world.html')
    # option={'xvfb': ''}
    # imgkit.from_file('/home/ubuntu/Backend/'+str(x)+'_world.html', str(x)+'_world.jpg')


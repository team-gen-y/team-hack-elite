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


def auto_open(path):
    html_page = f'{path}'
    new = 2
    webbrowser.open(html_page, new=new)


ur2 = "https://api.covid19india.org/csv/latest/state_wise.csv"
xt = pd.read_csv(ur2)
# print(xt.columns)
fin = xt.groupby('State')['Confirmed', 'Deaths', 'Recovered', 'Active', 'Last_Updated_Time'].max()
# print(fin)

lk = fin.reset_index()
# print(fin.iloc[:,:-1])
line = pd.DataFrame({"State": 'Daman and Diu', "Confirmed": lk.loc[7, "Confirmed"], "Deaths": lk.loc[7, "Deaths"],
                     "Recovered": lk.loc[7, "Recovered"], "Active": lk.loc[7, "Active"],
                     "Last_Updated_Time": lk.loc[7, "Last_Updated_Time"]}, index=[7.5])
print(line)
lk.loc[7, 'State'] = "Dadra and Nagar Haveli"
# lk.append(line,ignore_index=False)
# lk = lk.reset_index()
lk = lk.append(line, ignore_index=False)
lk = lk.sort_index().reset_index(drop=True)
lk = lk.drop(31)
lk = lk.drop(18)
lk = lk.drop(34)
lk['ID_1'] = range(1, len(lk['Confirmed']) + 1)
lk.loc[33, 'ID_1'] = 36
lk.loc[34:38, 'ID_1'] = lk.loc[34:38, 'ID_1'] - 1
print(lk.loc[:, ('State', 'ID_1')])

ur4 = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"
dat = json.load(urllib.request.urlopen(ur4))
json_data = lk.set_index('State').to_json()
json_data_final = json.dumps(json_data)
print(json_data_final)  # JSON Data for the Bar Graph of the state that I talked about yesterday


def state_map(params='Confirmed'):
    df = lk.loc[:, ('ID_1', params)]  # Params can be any of Confirmed, Active, Recovered and Deaths
    bins = list(df[params].quantile([0, 0.8, 0.9, 1]))
    colPal = {'Confirmed':'Greens','Recovered':'Blues','Deaths':'Reds','Active':'YlOrBr'}
    world_map = folium.Map(location=[21, 78], zoom_start=4, tiles='Mapbox Control Room')
    folium.Choropleth(
        geo_data=dat,
        data=df,
        columns=['ID_1', params],
        key_on='feature.properties.ID_1',
        fill_color=colPal[params],
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='COVID 19 ' + str(params) + ' Heat Map',
        bins=bins
    ).add_to(world_map)
    x = world_map
    return x


# options = Options()
# options.headless = True
# driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(600,600))
# display.start()

dats = ['Confirmed','Recovered','Deaths','Active']
for x in dats:
    state_map(x).save(str(x)+'.html')

    # option={'xvfb': ''}
    # imgkit.from_file('/home/ubuntu/Backend/'+str(x)+'.html',str(x)+'.jpg')
#     time.sleep(5)

#     driver.save_screenshot(str(x)+'.png')

# driver.quit()
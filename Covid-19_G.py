# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Sep 18 19:00:56 2021
# =============================================================================
# Data Scraping con Python: Datos de Covid-19 a nivel Mundial
# Author: Mayovar Alex Evanan (evananalex@gmail.com)
# Nota: Ejecutado en Python - Jupyter Lab con datos de Worldometer(2021) 
# =============================================================================


# =============================================================================
# 1. Requerimientos (Requirements)
# =============================================================================
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from datetime import date, datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as py
import seaborn as sns 
import gc 
import warnings
warnings.filterwarnings("ignore")


# =============================================================================
# 2. Optención de datos (Web Scraping) 
# =============================================================================

today = datetime.now()
print(today)
yesterday_str =  "%d %s, %d" %(today.day-1, date.today().strftime("%b"), today.year)
yesterday_str
# ---
url = "https://www.worldometers.info/coronavirus/#countries"
req = Request(url , headers ={'User-Agent': "Chrome/92.0.4515.159"})

webpage = urlopen(req)
print(webpage)
page_soup = soup(webpage, "html.parser")
page_soup.head()
# ---
table = page_soup.findAll("table",{"id":"main_table_countries_yesterday"})
containers = table[0].findAll("tr",{"style":""})
title = containers[0]
del containers[0]

all_data =[]
clean = True
for country in containers:
    country_data = []
    country_container = country.findAll("td")
    
    if country_container[1].text =="China":
        continue
    for i in range(1, len(country_container)):
        final_feature = country_container[i].text
        if clean:
            if i != 1 and i != len(country_container)-1:
                final_feature = final_feature.replace(",","")
                
                if final_feature.find('+') != -1:
                    final_feature = final_feature.replace("+","")
                    final_feature = float(final_feature)
                elif final_feature.find("-") != -1:
                    final_feature = final_feature.replace("-","")
                    final_feature = float(final_feature)*-1
        if final_feature == "N/A":
            final_feature = 0
        elif final_feature == "" or final_feature == " ":
            final_feature = -1
            
        country_data.append(final_feature)
        
    all_data.append(country_data)
# ---

# =============================================================================
# 3. Procesamiento de la data (Data Processing)
# =============================================================================
df = pd.DataFrame(all_data)
df
df.drop([15, 16, 17, 18, 19, 20], inplace = True, axis = 1)
column_labels = ["País","Total Casos","Nuevos Casos","Total Muertes","Nuevas Muertes","Total Recuperados","Nuevos Recuperados",
                 "Casos Activos","Serios/Críticos","Total Casos/1M","Muertes/1M","Total Tests","Tests/1M","Población","Continente"]
df.columns = column_labels
df
# ---
for label in df.columns:
    if label != 'País' and label != "Continente":
        df[label] = pd.to_numeric(df[label])
df
# ---

# =============================================================================
# 4. Exploración y análisis (Exploratory Data Analysis)
# =============================================================================

df["%Inc Casos"] = df["Nuevos Casos"]/df["Total Casos"]*100
df["%Inc Muertes"] = df["Nuevas Muertes"]/df["Total Muertes"]*100
df["%Inc Recuperados"] = df["Nuevos Recuperados"]/df["Total Recuperados"]*100
df

# --- A nivel mundial (Global)

cases = df[["Total Recuperados","Casos Activos","Total Muertes"]].loc[0]

cases_df = pd.DataFrame(cases).reset_index()
cases_df.columns = ["Tipo","Total"]

cases_df["Porcentaje"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID—19" for i in range(len(cases_df))]
#print(cases_df)

fig = px.bar(cases_df, x = "Virus", y = "Porcentaje", color = "Tipo", hover_data = ["Total"])
fig.update_layout(title={'text': "Total de casos Covid-19  según tipo a nivel mundial<br><sup>(Sep 2021)</sup>",
                         'y':0.95,
                         'x':0.5,
                         'xanchor': 'center',
                         'yanchor': 'top'},
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                 )

note = 'Elaboración propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.2,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )
fig.show()
# ---
cases = df[["Nuevos Recuperados","Nuevos Casos","Nuevas Muertes"]].loc[0]

cases_df = pd.DataFrame(cases).reset_index()
cases_df.columns = ["Tipo","Total"]

cases_df["Porcentaje"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID—19" for i in range(len(cases_df))]
#print(cases_df)

fig = px.pie(cases_df, names = "Tipo", values = "Porcentaje", hover_data = ["Total"])
fig.update_layout(title={'text': "Nuevos casos de Covid-19  según tipo a nivel mundial (%)<br><sup>(Sep 2021)</sup>",
                         'y':0.95,
                         'x':0.5,
                         'xanchor': 'center',
                         'yanchor': 'top'},
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                 )
note = 'Elaboración propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.20,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )

fig.show()
# ---
per = np.round(df[["%Inc Casos","%Inc Muertes","%Inc Recuperados"]].loc[0],2)

per_df = pd.DataFrame(per)
per_df.columns = ["Porcentaje"]

fig = go.Figure()

fig.add_trace(go.Bar(x = per_df.index, y = per_df["Porcentaje"], marker_color = ["cyan","orange", "limegreen"]))
fig.update_layout(title={'text': "Incremento de casos Covid-19 a nivel mundial<br><sup>(Sep 2021)</sup>",
                         'y':0.85,
                         'x':0.5,
                         'xanchor': 'center',
                         'yanchor': 'top'},
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                 )

note = 'Elaboración propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.20,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )

fig.show()

# --- Continentes (By Continents)

continent_df = df.groupby("Continente").sum().drop("All")
continent_df = continent_df.reset_index()
continent_df
# ---
note = 'Elaboración propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'

def continent_visualization(vis_list):
    for label in vis_list:
        c_df = continent_df[['Continente', label]]
        c_df["Porcentaje"] = np.round(100*c_df[label]/np.sum(c_df[label]),2)
        c_df["Virus"] = ['Covid — 19' for i in range(len(c_df))]
        
        
        fig = px.bar(c_df, 
                     x= 'Continente', 
                     y= 'Porcentaje', 
                     color= 'Continente',
                     hover_data=[label])
        fig.update_layout(title={'text':f"{label} <br><sup>(Actualizado al {yesterday_str})</sup>",
                                 'y':0.95,
                                 'x':0.5,
                                 'xanchor': 'center',
                                 'yanchor': 'top'},
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                         )
        
        fig.add_annotation(text=note,
                           font=dict(size=11),
                           align="left",
                           x=0.0,
                           y=-0.20,
                           xref="x domain",
                           yref="y domain",
                           showarrow=False,
                          )
        
        fig.show()
        gc.collect()
# ---
cases_list = ["Total Casos","Casos Activos", "Nuevos Casos", "Serios/Críticos", "Total Casos/1M", "%Inc Casos"]
deaths_list = ["Total Muertes","Nuevas Muertes", "Muertes/1M", "%Inc Muertes"]
recorvered_list = ["Total Recuperados", "Nuevos Recuperados", "%Inc Recuperados" ]

# ---
continent_visualization(cases_list)
# ---
continent_visualization(deaths_list)
# ---
continent_visualization(recorvered_list)

# --- Países (By Countries)

df = df.drop(len(df)-1)
country_df = df.drop([0])

country_df
# ---
LOOK_AT = 5
country = country_df.columns[1:14]

fig = go.Figure()
c = 0
for i in country_df.index:
    if c < LOOK_AT:
        fig.add_trace(go.Bar(name= country_df['País'][i], x= country, y= country_df.loc[i][1:14]))
    else:
        break
    c +=1
    
fig.update_layout(title = {'text':f'Top {LOOK_AT} de países a nivel mundial con casos de Covid-19<br><sup>(Actualizado al {yesterday_str})</sup>',
                           'y':0.9,
                           'x':0.5,
                           'xanchor': 'center',
                           'yanchor': 'top' },
                  yaxis_type = "log",
                  legend_title="Países",
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                 )

note = 'Elaboración propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.25,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )

fig.show()

# --- América del Sur (South America)

south_df = country_df.loc[country_df["Continente"] == "South America"].reset_index()
south_df = south_df.drop(columns=["index"])
print("Dimension of table",south_df.shape)
south_df
# ---
LOOK_AT = 5
south = south_df.columns[1:14]

fig = go.Figure()
c = 0
for i in south_df.index:
    if c < LOOK_AT:
        fig.add_trace(go.Bar(name= south_df['País'][i], x= country, y= south_df.loc[i][1:14]))
    else:
        break
    c +=1
    
fig.update_layout(title = {'text':f'Top {LOOK_AT} de países de América del Sur por casos de Covid-19<br><sup>(Actualizado al {yesterday_str})</sup>',
                           'y':0.9,
                           'x':0.5,
                           'xanchor': 'center',
                           'yanchor': 'top' }, 
                  yaxis_type = "log",
                  legend_title="Países",
                  font=dict(family="Franklin Gothic",
                            size = 14,
                            color="black")
                 )
note = 'Elaboracion Propia <br>Fuente: Con datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a>'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.25,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )

fig.show()
# ---
south_df1 = south_df.loc[south_df["Muertes/1M"] > 0]

fig = px.scatter(south_df1, x="Total Casos", y="Población",
                 size="Muertes/1M", color="País",
                 hover_name="País", log_x=True, size_max=60)

fig.update_layout(
    title={
        'text': "Población vs Total de casos Covid-19 en Sudamérica <br><sup>(Tamaño determinado por Muertes por millón, Sep 2021)</sup> ",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        legend_title="Países",
        font=dict(family="Franklin Gothic",
                  size = 13,
                  color="black")
    )
note = 'Elaboración propia <br>Fuente: Datos de <a href="https://www.worldometers.info/coronavirus/#countries">Worldometers</a> (2021)'
fig.add_annotation(text=note,
                   font=dict(size=11),
                   align="left",
                   x=0.0,
                   y=-0.2,
                   xref="x domain",
                   yref="y domain",
                   showarrow=False,
                  )

fig.show()
# =============================================================================
# =============================================================================
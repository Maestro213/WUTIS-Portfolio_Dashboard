import streamlit as st
import numpy as np
import pandas as pd
import pandas_ta as ta
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import json
from datetime import datetime
import altair as alt
from streamlit_lottie import st_lottie
import yfinance as yf
# For plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px





st.set_page_config(layout='wide', page_title='Stock Dashboard', page_icon=':dollar:')

#######################
# Sidebar
st.sidebar.header("WUTIS Investmnt Strategies")
d = ["General", "Equity Research", "Global Markets", "Algorithmic Trading"]
Department = st.sidebar.selectbox('Department', d, index=0)

COLOR_BULL = 'rgba(38,166,154,0.9)' # #26a69a
COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350


df1 = pd.read_csv(r'data/ER.csv',index_col=0)
df1 = df1.reset_index()
df1['Date']= pd.to_datetime(df1['Date']).dt.date




    

# Calculate the MAs for graphs
df1['SMA-50'] = df1['Cumulative Return'].rolling(50).mean().dropna()
df1['SMA-200'] = df1['Cumulative Return'].rolling(200).mean().dropna()
# calculate the prior peaks for each day in our dataset
df1["Prior Peak"] = df1['Cumulative Return'].cummax()
# calculate the drawdown
df1["Drawdown"] = (df1['Cumulative Return'] - df1["Prior Peak"]) / df1["Prior Peak"]
#Calculating the Metrics 
ret = round((1+df1.Return).prod()-1,4) * 100 
vol =  round(df1.Return.std(),2)
rf = 0.04**(1/2)
sharpe_ratio = round((ret-0.04**(1/2))/vol,2)
max_drawdown = round(df1["Drawdown"].min(),2)
var =  -np.percentile(df1['Cumulative Return'], (100 - level))
met = pd.DataFrame({"Returns":ret, "Volatility":vol,"Sharpe Ratio": sharpe_ratio, "Maximum Drawdown":max_drawdown, "VaR":var},index=[0])

df = pd.concat([df1['Cumulative Return'],df1['SMA-50']],axis = 1).dropna()
#######################
# Dashboard Main Panel
col = st.columns((8, 12), gap='medium')
with col[0]:
    st.markdown('#### Perfomance')

    st.dataframe(met,
                 column_order=("Returns","Volatility","Sharpe Ratio" ),
                 hide_index=True,
                 width=None,)
    st.dataframe(df1.tail(10))
    

#######################
# Plot
with col[1]:
    fig = px.line(df1, x="Date", y=df.columns, title='WUTIS Portfolio')
  
    fig.show()
    

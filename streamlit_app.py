import streamlit as st
import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import yfinance as yf
# For plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import altair as alt




st.set_page_config(layout='wide', page_title='Stock Dashboard', page_icon=':dollar:')

#######################
# Sidebar
st.sidebar.header("WUTIS Investmnt Strategies")
d = ["General", "Equity Research", "Global Markets", "Algorithmic Trading"]
Department = st.sidebar.selectbox('Department', d, index=0)

COLOR_BULL = 'rgba(38,166,154,0.9)' # #26a69a
COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350


df_er = pd.read_csv(r'data/ER.csv',index_col=0)
df_gm = pd.read_csv(r'data/GM.csv',index_col=0)
df_algo = pd.read_csv(r'data/Algo.csv',index_col=0)



    
def metrics(df, av_capital = 300000):
    #this function calculate the metrics such as: Ann Ret, Ann Volatility, Sharpe ration, Maximum Drawdown, VaR
    df.reset_index(inplace=True)
    df['Date']= pd.to_datetime(df['Date']).dt.date
    df['Return Pct'] = df["Adj Close"].pct_change()
    df['Return Pct'][0] = 0
    df['Return'] = df['Return Pct'] * av_capital
    df['Cumulative Return Pct'] = (1 + df['Return Pct']).cumprod() 
    df['Cumulative Return'] = (1 + df['Return Pct']).cumprod() * av_capital
    
    #Maximum Drawdown
    # calculate the prior peaks for each day in our dataset
    df["Prior Peak"] = df['Cumulative Return'].cummax()
    # calculate the drawdown
    df["Drawdown"] = (df['Cumulative Return'] - df["Prior Peak"]) / df["Prior Peak"]
    max_drawdown = round(df["Drawdown"].min(),2)
    n_periods = df.shape[0]
    #Ann Return 
    ret = round((1+df["Return Pct"]).prod()**(252/n_periods)-1,4) * 100 
    #Ann Volatility
    vol =  round(df["Return Pct"].std()*(252**0.5),2)
    rf = 0.04**(1/2)
    #Sharpe Ratio
    sharpe_ratio = round((ret-0.04**(1/2))/vol,2)
    
    var = round( -np.percentile(df['Return'], (100 - 5)),2)
    
    met = pd.DataFrame({"Returns":ret, "Volatility":vol, "Sharpe Ratio": sharpe_ratio, "Maximum Drawdown":max_drawdown, "VaR":var},index=[0])
    return met, df

sp = yf.download("SPY", start = "2023-09-30", end = "2024-03-01")
sp_met, sp = metrics(sp)
er_met, df_er = metrics(df_er)
gm_met, df_gm = metrics(df_gm)
algo_met, df_algo = metrics(df_algo)


df = pd.concat([df_er.Date, df_er['Cumulative Return'],df_gm['Cumulative Return'],df_algo['Cumulative Return'],sp['Cumulative Return']],axis = 1).dropna()
df = df.set_axis(["Date","Equity Research", "Global Markets", "Algorithmic Trading",'S&P500 Benchmark'],axis=1)

## Add to the whole portfolio
df["WUTIS"] = df[["Equity Research", "Global Markets", "Algorithmic Trading"]].sum(axis=1)
met = pd.concat([er_met, gm_met, algo_met,sp_met],axis = 0)
met = met.set_axis(["Equity Research", "Global Markets", "Algorithmic Trading",'S&P500 Benchmark'],axis=0)
#######################
# Dashboard Main Panel

fig = px.line(df, x="Date", y=["WUTIS", "Equity Research", "Global Markets", "Algorithmic Trading",'S&P500 Benchmark'], title='WUTIS Portfolio')
fig.show()

col = st.columns((8, 12), gap='medium')


with col[0]:
    st.markdown('#### Perfomance')
    st.dataframe(met, hide_index=True, width=None,)
    st.dataframe(df.tail(10))
 

#######################
# Plot
with col[1]:
    st.markdown("Portfolio Perfomance")
    st.line_chart(df, x='Date', y=['WUTIS', 'Equity Research', 'Global Markets', 'Algorithmic Trading', 'S&P500 Benchmark'])
    a = alt.Chart(df).mark_area(opacity=1).encode(x='Date', y=['Equity Research', 'Global Markets', 'Algorithmic Trading', 'S&P500 Benchmark'])
    b = alt.Chart(df).mark_area(opacity=0.6).encode(x='Date', y='WUTIS')
    c = alt.layer(a, b)
    st.altair_chart(c, use_container_width=True)



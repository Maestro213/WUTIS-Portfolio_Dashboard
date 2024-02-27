import streamlit as st
import numpy as np
import pandas as pd
import pandas_ta as ta
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import json
import altair as alt
from streamlit_lottie import st_lottie
import yfinance as yf



st.sidebar.header("WUTIS Investmnt Strategies")
d = ["General", "Equity Research", "Global Markets", "Algorithmic Trading"]
Department = st.sidebar.selectbox('Department', d, index=0)

Ticker = "MSFT"
COLOR_BULL = 'rgba(38,166,154,0.9)' # #26a69a
COLOR_BEAR = 'rgba(239,83,80,0.9)'  # #ef5350


def read_yf(Ticker):
    # print('Start date: {}'.format(start_date))
    df = pd.DataFrame()
    try:
        df = yf.Ticker(Ticker).history(period='6mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    except Exception as e:
        print("The error is: ", e)
    if not df.empty:
        # Create a Date column
        df['Date'] = df.index.date
        # Drop the Date as index
        df.reset_index(drop=True, inplace=True)
        # Some data wrangling to match required format
        df.columns = ['time','open','high','low','close','volume']                  # rename columns
        df['color'] = np.where(  df['open'] > df['close'], COLOR_BEAR, COLOR_BULL)  # bull or bear
        df.ta.macd(close='close', fast=6, slow=12, signal=5, append=True)           # calculate macd
        # Added extra columns
        #df['Ticker'] = st.session_state.ticker
        df['Refreshed Date'] = datetime.now()
    return df


df = read_yf(Ticker)


candles = json.loads(df.to_json(orient = "records"))
volume = json.loads(df.rename(columns={"volume": "value",}).to_json(orient = "records"))
macd_fast = json.loads(df.rename(columns={"MACDh_6_12_5": "value"}).to_json(orient = "records"))
macd_slow = json.loads(df.rename(columns={"MACDs_6_12_5": "value"}).to_json(orient = "records"))
df['color'] = np.where(  df['MACD_6_12_5'] > 0, COLOR_BULL, COLOR_BEAR)  # MACD histogram color
macd_hist = json.loads(df.rename(columns={"MACD_6_12_5": "value"}).to_json(orient = "records"))

chartMultipaneOptions = [
    {
        "width": 600,
        "height": 400,
        "layout": {
            "background": {
                "type": "solid",
                "color": 'transparent'
            },
            "textColor": "white"
        },
        "grid": {
            "vertLines": {
                "color": "rgba(197, 203, 206, 0.5)"
                },
            "horzLines": {
                "color": "rgba(197, 203, 206, 0.5)"
            }
        },
        "crosshair": {
            "mode": 0
        },
        "priceScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)"
        },
        "timeScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)",
            "barSpacing": 15
        },
        "watermark": {
            "visible": True,
            "fontSize": 48,
            "horzAlign": 'center',
            "vertAlign": 'center',
            "color": 'rgba(171, 71, 188, 0.3)',
            "text": f'{Ticker}',
        }
    },
    {
        "width": 600,
        "height": 100,
        "layout": {
            "background": {
                "type": 'solid',
                "color": 'transparent'
            },
            "textColor": 'white',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(42, 46, 57, 0)',
            },
            "horzLines": {
                "color": 'rgba(42, 46, 57, 0.6)',
            }
        },
        "timeScale": {
            "visible": False,
        },
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'top',
            "color": 'rgba(171, 71, 188, 0.7)',
            "text": 'Volume',
        }
    },
    {
        "width": 600,
        "height": 200,
        "layout": {
            "background": {
                "type": "solid",
                "color": 'transparent'
            },
            "textColor": "white"
        },
        "timeScale": {
            "visible": False,
        },
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'center',
            "color": 'rgba(171, 71, 188, 0.7)',
            "text": 'MACD',
        }
    }
]

seriesCandlestickChart = [
    {
        "type": 'Candlestick',
        "data": candles,
        "options": {
            "upColor": COLOR_BULL,
            "downColor": COLOR_BEAR,
            "borderVisible": False,
            "wickUpColor": COLOR_BULL,
            "wickDownColor": COLOR_BEAR
        }
    }
]

seriesVolumeChart = [
    {
        "type": 'Histogram',
        "data": volume,
        "options": {
            "priceFormat": {
                "type": 'volume',
            },
            "priceScaleId": "" # set as an overlay setting,
        },
        "priceScale": {
            "scaleMargins": {
                "top": 0,
                "bottom": 0,
            },
            "alignLabels": False
        }
    }
]

seriesMACDchart = [
    {
        "type": 'Line',
        "data": macd_fast,
        "options": {
            "color": 'blue',
            "lineWidth": 2
        }
    },
    {
        "type": 'Line',
        "data": macd_slow,
        "options": {
            "color": 'green',
            "lineWidth": 2
        }
    },
    {
        "type": 'Histogram',
        "data": macd_hist,
        "options": {
            "color": 'red',
            "lineWidth": 1
        }
    }
]


renderLightweightCharts([
    {
        "chart": chartMultipaneOptions[0],
        "series": seriesCandlestickChart
    },
    {
        "chart": chartMultipaneOptions[1],
        "series": seriesVolumeChart
    },
    {
        "chart": chartMultipaneOptions[2],
        "series": seriesMACDchart
    }
], 'multipane')

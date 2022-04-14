# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 10:37:42 2022



@author: Barun sharma
"""



import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import time
#import requests
#import io
#import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import talib
import copy

import login as l
import ks_api_client 
from ks_api_client import ks_api 
import requests

client = ks_api.KSTradeApi(access_token = l.access_token, userid = l.userid, \
                    consumer_key = l.consumer_key, ip = "127.0.0.1", app_id = l.app_id)
    
client.login(password = l.password)
client.session_2fa(access_code = l.access_code)


def todayposition():
    msg = pd.DataFrame(client.positions(position_type= "TODAYS"))
    p = msg["Success"][0]
    print(f"P/L : {p['netChange']}")
    print(f"P/L with tax : {((p['buyTradedVal']+p['sellTradedVal'])*0.0004/2)-p['netChange']}")
    print(f"BUY QTY : {p['buyTradedQtyLot']}")
    print(f"BUY VALUE : {p['buyTradedVal']}")
    print(f"SELL QTY : {p['sellTradedQtyLot']}")
    print(f"SELL VALUE : {p['sellTradedVal']}")




######################################################################
def trade_execute():
    live_data = {'ltp':[]}
    position = None
    token = 1829
    bslp=0.999 #buy stop loss percent
    sslp = 1.001 ##sell stop loss percent
    entry_price = 0
    buySL = entry_price*bslp
    sellSL = entry_price*sslp
    
    
    
    
    def BUY(lp):
        client.place_order(order_type = "N", instrument_token = token, transaction_type = "BUY",\
                           quantity = 1, price = lp , disclosed_quantity = 0, trigger_price = 0,\
                                validity = "GFD", variety = "REGULAR", tag = "string")
    def SELL(lp):
        client.place_order(order_type = "N", instrument_token = token, transaction_type = "SELL",\
                               quantity = 1, price = lp , disclosed_quantity = 0, trigger_price = 0,\
                                    validity = "GFD", variety = "REGULAR", tag = "string")

    for i in range(1,27):
        msg = client.quote(instrument_token = token)
        df = msg["success"][0]
        lp = float(df["ltp"])
        live_data["ltp"].append(lp)
        time.sleep(1)


    while datetime.time(15,10) > datetime.datetime.now().time():
        try:          
            msg = client.quote(instrument_token = token)
            df = msg["success"][0]
            lp = float(df["ltp"])
            live_data["ltp"].append(lp)
            fast_average=sum(live_data["ltp"][-9:])/9
            slow_average=sum(live_data["ltp"][-10:])/10
            
            if lp*bslp>buySL:
                buySL = lp*bslp
        
            if lp*sslp<sellSL:
                sellSL = lp*sslp
                
            print(f"ltp :{lp},Entry price : {entry_price} ,buySL : {buySL},sellSL : {sellSL} ,fast:{fast_average} ,slow:{slow_average}")
            
            if not position:
                if fast_average>slow_average:
                    #buy code
                    #BUY(lp)
                    
                    position = "Buy"
                    print(f"Entry buy : {lp}")
                    entry_price = lp

                if fast_average<slow_average:
                    #sell code
                    #SELL(lp)
                    position = "Sell"
                    print(f"Entry sell : {lp}")
                    entry_price = lp
                    
            if position == "Buy" and lp<=buySL:
                
                    #SELL(lp)
                    
                    position = None
                    print(f"Exit Buy by sellig on : {lp}")

            if position == "Sell" and lp >= sellSL:
                    #BUY(lp)
                    
                    position = None
                    print(f"Exit sell by buying on : {lp}")

            time.sleep(15)


        except Exception as e:
            print("Exception when calling QuoteApi->quote_details: %s\n" % e)
            break
            time.sleep(10)
#######################################################################
#todayposition()

trade_execute()



try:
    # Invalidate Session Tsoken
    client.logout()
except Exception as e:
    print("Exception when calling SessionApi->logout: %s\n" % e)



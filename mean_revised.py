"""
#Akkarawat Mansap
#Credit1 : Nattapon Soomtha (กองทุนความมั่งคั่งแห่งชาติ Training)
#Credit2 : b2 spetsnaz club
#Credit3 : TEERACHAI RATTANABUNDITSAKUL
#----------------------------------------------------------------
# 1. 코인구매 및 주문 확인(코인 판매)에 필요한 Install library가 필요합니다.
# - 다양한 Exchange에 API를 쉽게 연결할 수 있는 인기 있는 ccxt library가 있습니다.
# - Pandas library는 Exchange에서 추출한 데이터를 변환하는 데 도움이 됩니다.
# - 주문 확인을 쉽게 할 수 있는 테이블입니다.
# - json은 Exchange에서 필요한 정보를 추출하는 데 사용됩니다.
# - pip로 시작하는 것을 다운로드 하세요.
#!pip install ccxt
#!pip install pandas
"""

# Config Session

import ccxt
import json
import pandas as pd
import time

# api and secret

apiKey = ''         #input("Enter API Key:")      
secret = ''         #input("Enter Secret Key:")
subaccount = ''                                      #input("Enter Sub Account Name or 0 for Main:")


# Exchange Detail
exchange = ccxt.ftx({
    'apiKey' : apiKey ,'secret' : secret ,'enableRateLimit': True
})

# Sub Account Check

if subaccount == "0":
  print("This is Main Account")
else:
  exchange.headers = {
   'FTX-SUBACCOUNT': subaccount,
  }

# Global Variable Setting
pair = 'BTC-PERP' # 자기가 원하는 코인
tf = '5m'

# Get Price Hist Data

def priceHistdata():
  
  try:
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except ccxt.NetworkError as e:
    print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except ccxt.ExchangeError as e:  
    print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except Exception as e:
    print(exchange.id, 'fetch_ohlcv failed with:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))

  return priceData
  
# Variable setting for minimum Range and minimum Profit
buyRecord = []
minimumRange = 10
minimumProfit = 30
minOrder = min(buyRecord, default=0.0)
maxOrder = max(buyRecord, default=100000000.0)
priceData = priceHistdata()
buySignal = round((priceData.iloc[-31:-1,4].mean())*2) / 2
sellSignal = round((priceData.iloc[-11:-1,4].mean())*2) / 2

def getPrice():

  try:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
    #print(exchange)
    #print(pair + '=',dataPrice['last'])
  except ccxt.NetworkError as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  except ccxt.ExchangeError as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  except Exception as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  
  return (dataPrice['last'])

def showPending():
    print("Your Pending Order")
    pendingOrder = pd.DataFrame(exchange.fetch_open_orders(pair),
                   columns=['id','datetime','status','symbol','type','side','price','amount','filled','average','remaining'])
    pendingOrder.head(5)
    return pendingOrder

def showMatched():
    print("Your Matched Order")
    matchedOrder = pd.DataFrame(exchange.fetchMyTrades(pair),
                       columns=['id','datetime', 'symbol','type','side','price','amount','cost'])
    print(matchedOrder.head(5))
    return matchedOrder

def sendBuy():
  types = 'limit'                         # 유형
  side = 'buy'                            # 구매/판매
  usd = 1                                 # Rebalance의 경우 USD로 입력해야 합니다.
  price = buySignal + 20                  # 원하는 가격 수준(구매)
  size_order = usd/price                  # BTC로 구매 하고 싶다면, usd/price를 #로 입력하고 대신 usd 변수에 입력하세요
  reduceOnly = False                      # 사용 가능한 개수만큼만 포지션을 닫습니다. (CREDIT : TY)
  postOnly =  False                       # 포지션을 MAKER로만 배치합니다.
  ioc = False                             
                                          
  ## Send Order ##
  exchange.create_order(pair, types , side, size_order, price)

  ## Show Order Status##
  print("     ")
  showPending()
  print("     ")
  showMatched()

def sendSell():
  types = 'limit'                         # 유형
  side = 'sell'                           # 구매/판매
  usd = 1                                 # Rebalance의 경우 USD로 입력해야 합니다.
  price = sellSignal - 20                 # 원하는 가격 수준(구매)
  size_order = usd/price                  # BTC로 구매 하고 싶다면, usd/price를 #로 입력하고 대신 usd 변수에 입력하세요
  reduceOnly = True                       # 사용 가능한 개수만큼만 포지션을 닫습니다. (CREDIT : TY)
  postOnly =  False                       # 포지션을 MAKER로만 배치합니다.
  ioc = False                             

  ## Send Order ##
  exchange.create_order(pair, types , side, size_order, price)

  ## Show Order Status##
  print("     ")
  showPending()
  print("     ")
  showMatched()

def readOrder():
  #Read Order To file
  with open("list.txt", "r") as f:
    for line in f:
      buyRecord.append(float(line.strip()))
  print(buyRecord)

def writeOrder():
  with open("list.txt", "w") as f:      #Write Order To file 
    for ord in buyRecord:
      f.write(str(ord) +"\n")

# LOGIC SESSION

def checkBuycondition():

  # Buy Condition
  if getPrice() == buySignal and len(buyRecord) <= 30 and buyRecord.count(buySignal) < 1:
    if (minOrder - getPrice()) > minimumRange or (getPrice() - maxOrder) > 10 or len(buyRecord) < 1 :
      sendBuy()
      print('Buy 1 USD at' + str(buySignal))
      buyRecord.append(buySignal)
      writeOrder()

    else:
      print('Not enough minimum Range = ' + str(minimumRange))
  else:
    print(getPrice())
    print('waiting for buy signal ' + 'at ' + str(buySignal))


def checkSellcondition():

  # Sell Signal function
  if len(buyRecord) > 0:
    if getPrice() <= sellSignal and getPrice() - minOrder > 0 :
      print('sell signal triggered at ' + str(sellSignal)) 
      for ord in buyRecord:
        if getPrice() - ord > minimumProfit:
          sendSell()
          buyRecord.remove(ord)
          print(buyRecord)
          writeOrder()
        else:
          print('Not Enough Profit ' + 'Minimum = ' + str(ord + minimumProfit))
          
    else:
      print('Waiting for last minimum order ' + 'at ' + str(minOrder))
  else: print('No Buy Order Record')
  print("  ")



# Execute Session

while True:
  buyRecord = []
  priceData = priceHistdata()
  buySignal = round((priceData.iloc[-31:-1,4].mean())*2) / 2
  sellSignal = round((priceData.iloc[-11:-1,4].mean())*2) / 2
  print(time.ctime())
  readOrder()
  minOrder = min(buyRecord, default=0.0)
  maxOrder = max(buyRecord, default=100000000.0)
  getPrice()
  checkBuycondition()
  checkSellcondition()
  time.sleep(1)

  
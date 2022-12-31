from datetime import datetime
from yahoo_fin import stock_info as si
import json
from math import cos
from math import pi
from asciichartpy import plot

f = open("BROADTAPE.csv", "a")

textfile = ''
#Print Date
dt = datetime.now()
textfile += (dt.strftime("%A %b %d, %Y").upper())

#Add Space
textfile += ('\n')

#Time
textfile += (dt.strftime("%X E.S.T.").upper())

#Space
textfile += ('\n')


textfile += ('-------------------------DOW JONES-------------------------\n\n')

textfile += ('US STOCK INDICES\n\n')
textfile += ('DOW JONES INDUSTRIALS $' + str(si.get_live_price('YM=F')))
textfile += '\n'
textfile += ('STANDARD & POORS 500 $' + str(si.get_live_price('SP=F')))
textfile += '\n'
textfile += ('NASDAQ 100 $' + str(si.get_live_price('NQ=F')))
textfile += '\n'
textfile += ('CBOE VOLATILITY INDEX $' + str(si.get_live_price('^VIX')))
textfile += '\n'

with open('Modified Data/SPY/SPY_RAWDATA.json') as f:
  data = json.load(f)
  #MOST RECENT EXPECTATION
  change = str((((data[len(data)-1]['expectation'])-data[len(data)-20]['expectation'])/data[len(data)-20]['expectation'])*10000)
  textfile += (str('SPY SENTIMENT '+str(data[len(data)-1]['expectation']) + " " + change + "%"))
  textfile += '\n'
textfile += ('\n')

textfile += ('US COMMODITIES\n')
textfile += '\n'
textfile += ('GOLD $' + str(si.get_live_price('GC=F')))
textfile += '\n'
textfile += ('SILVER $' +str(si.get_live_price('SI=F'))) 
textfile += '\n'
textfile += ('WTI CRUDE OIL $' +str(si.get_live_price('Cl=F')))
textfile += '\n'
textfile += ('COAL $' +str(si.get_live_price('MTF=F'))) 
textfile += '\n'
textfile += ('WHEAT $' +str(si.get_live_price('ZW=F')))
textfile += '\n'
textfile += ('COFFEE $' +str(si.get_live_price('KC=F'))) 
textfile += '\n'
textfile += ('COCOA $' +str(si.get_live_price('CC=F'))) 
textfile += '\n'
textfile += ('LUMBER $' +str(si.get_live_price('LBS=F'))) 
textfile += '\n'
textfile += ('ORANGE JUICE $' +str(si.get_live_price('OJ=F')))
textfile += '\n'
textfile += ('\n')

textfile += ('US BONDS\n')
textfile += '\n'
textfile += ('SHORT TREASURY $' + str(si.get_live_price('SHV')))
textfile += '\n' 
textfile += ('10 YEAR TREASURY $' + str(si.get_live_price('IEF')))
textfile += '\n'
textfile += ('30 YEAR TREASURY $' + str(si.get_live_price('^SYX'))) 
textfile += '\n'
textfile += ('HIGH YIELD CORPORATE BOND $' + str(si.get_live_price('MTF=F'))) 
textfile += '\n'
textfile += ('HIGH YIELD CORPORATE BOND $' + str(si.get_live_price('ZW=F'))) 
textfile += '\n'
textfile += ('\n')

textfile += ('FOREIGN EXCHANGE RATE\n')
textfile += '\n'
textfile += ('BRITISH POUND ' + str(si.get_live_price('GBPUSD=X'))) 
textfile += '\n'
textfile += ('CANADIAN DOLLAR ' + str(si.get_live_price('CADUSD=X'))) 
textfile += '\n'
textfile += ('EURO ' + str(si.get_live_price('EURUSD=X'))) 
textfile += '\n'
textfile += ('SWISS FRANC ' + str(si.get_live_price('CHFUSD=X'))) 
textfile += '\n'
textfile += ('\n')

textfile += ('PORTFOLIO SELECTED\n')
textfile += '\n'
textfile += ('PROSHARES ULTRA VIX SHORT-TERM FUT ETF $' + str(si.get_live_price('UVXY'))) 
textfile += '\n'

f.write(textfile)
f.close()
from yahoo_fin import stock_info as si
import matplotlib
import matplotlib.pyplot as plt
import requests
from datetime import datetime as dt, timezone
from datetime import datetime 
from csv import reader
import csv
import json
from bson import json_util
import time
currentMonth = datetime.now().month
images = {'expectation_change', 'real_change', 'index', 'bear_count', 'bull_count', 'raw_expectations', 'expectation'}
dates = {}

#GET THESE LIVE PRICES AT 4:00 everyday AND SAVE IT TO GET PERCENT CHANGES FOR THE NEXT MORNING
##API REFERENCE 
##US STOCK INDICIES
##si.get_live_price('YM=F') DOW JONES INDUSTRIALS 
##si.get_live_price('SP=F') STANDARD & POORS 500
##si.get_live_price('NQ=F') NASDAQ 100
##si.get_live_price('SP=F') STANDARD & POORS 500
##si.get_live_price('^VIX') VOLATILITY INDEX
##'EXPECTATION' S&P 500 SENTIMENT  

##US COMMODITIES
##si.get_live_price('GC=F') GOLD
##si.get_live_price('SI=F') SILVER
##si.get_live_price('Cl=F') WTI CRUDE OIL
##si.get_live_price('MTF=F') COAL
##si.get_live_price('ZW=F') WHEAT
##si.get_live_price('KC=F') COFFEE
##si.get_live_price('LBS=F') COCOA
##si.get_live_price('LBS=F') LUMBER
##si.get_live_price('OJ=F') ORANGE JUICE

##US BOND
##si.get_live_price('SHV') SHORT TREASURY
##si.get_live_price('IEF') 10 YEAR TREASURY
##si.get_live_price('^SYX') 30 YEAR TREASURY
##si.get_live_price('MTF=F') HIGH YIELD CORPORATE BOND
##si.get_live_price('ZW=F') HIGH GRADE CORPORATE BOND

##FOREIGN EXCHANGE RATE
##si.get_live_price('GBPUSD=X') USD/GBP
##si.get_live_price('CATUSD=X') USD/CAT
##si.get_live_price('EURUSD=X') USD/EUR
##si.get_live_price('CHFUSD=X') USD/CHF

##PORTFOLIO SELECTED
##si.get_live_price('UVXY') UVXY
##VOLUME

#NEED AUTOMATIC UPDATE OF FILES AT CERTAIN TIME - NEXT MORNING @ 7? 
##MAYBE IN SEPARATE PROGRAM
def getData(months, years, ticker):
    data = []
    yearind = 1
    subtract = 0
    for x in range(1, int(currentMonth) + int(months)):
        print(x)
        
        if x == currentMonth + 1:
            print('current mm')
            yearind = yearind + 1 
            subtract = subtract + currentMonth
        if (x-subtract) % 13 == 0 and x != 1: 
            print('every thirteen')
            yearind = yearind + 1 
            subtract = subtract + currentMonth
            if x > 2:
                subtract = subtract + 2
        print(subtract)
        print("Ticker: " + str(ticker) + " Year: " + str(yearind) + " Month: " + str(x-subtract))
        data.append(int(x-subtract))
        # MUST CREATE FOLDER
        f = open('Data/' + ticker + '/' + ticker + '-RAW_DATA' + ".csv", "a")
        res = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=' + str(ticker) + '&interval=30min&slice=year' + str(yearind) + 'month' + str(x-subtract) + '&apikey=this_is_api_key')
        f.write(res.text)
        
        f.close()
        #Stop at TWO years
        twoyear = datetime.now() - dt.timedelta(days=2*365) #doesnt work
        #See if date, as they come in, if it is the date from 2 years ago. If so, stop the loop
        #OR - If date in data is equal to twoyear, then stop the loop
        time.sleep(11)

def main():
    t = input("Enter Ticker: ")
    years = input('Enter Number of Years(Excluding this year): ')

    print("You entered: " + t)

    getData((years*12), years, t)

    transformRawData(t)

def transformRawData(ticker):
    #this kind of does
    with open('Data/' + ticker + '/' + ticker +  '.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            if row[0] == 'time':
                continue

            datetime = dt.strptime(row[0], "%Y-%m-%d %H:%M:%S") # fmt: 2020-09-15 16:00:00
            timestamp = datetime.replace(tzinfo=timezone.utc).timestamp()
            at_date = datetime.date()
            at_time = datetime.time()
            date_str = str(at_date)

            # make it a dict
            dates[date_str] = dates.get(date_str, {
            'timestamp': timestamp,
            'date_str': dt.combine(at_date, dt.min.time()).strftime("%Y-%m-%d %H:%M:%S"),
            'date': dt.combine(at_date, dt.min.time())
            })

                # Time @ 4:00
            if at_time.hour == 16 and at_time.minute == 0 and at_time.second == 00:
                dates[date_str]['closed_at'] = float(row[4])

            # Time @ 3:30
            if at_time.hour == 15 and at_time.minute == 30 and at_time.second == 00:
                dates[date_str]['open_at'] = float(row[4])

    # print(dates)

    instances = list(dates.values())
    instances.sort(key=lambda x: x['timestamp'])

    def percent_change(initial, final):
        return (float(final) - float(initial)) / float(final)

    out = []
    for (i, today) in enumerate(instances):
        print(today['date_str'])
        print(today)
        if 'closed_at' not in today and 'open_at' in today:
            today['closed_at'] = today['open_at']
        elif 'open_at' not in today and 'closed_at' in today:
            today['open_at'] = today['closed_at']
        elif 'open_at' not in today and 'closed_at' not in today:
            print('missing data!')
            continue

        if i == 0:
            today['open_at'] = today['closed_at']
            today['expectation'] = today['closed_at']
            today['index'] = today['closed_at']
            today['expectation_change'] = 0.0
            today['real_change'] = 0.0
            today['adjusted_real_change'] = 0.0
            today['bear_bull_ratio'] = 0.0
            today['raw_expectations'] = 0.0
            today['bear_count'] = 0.0
            today['bull_count'] = 0.0
        else:
            yesterday = instances[i-1]
            today['expectation_change'] = percent_change(today['open_at'], today['closed_at'])
            today['expectation'] = (yesterday['expectation'] / 100.0 * today['expectation_change']) + yesterday['expectation']
            today['index'] = today['closed_at']
            today['real_change'] = percent_change(yesterday['closed_at'], today['closed_at'])
            yesterday['adjusted_real_change'] = percent_change(yesterday['closed_at'], today['closed_at'])

            today['bear_count'] = yesterday['bear_count']
            today['bull_count'] = yesterday['bull_count']

            if today['expectation_change'] < 0:
                today['bear_count'] += 1
                today['raw_expectations'] = yesterday['raw_expectations'] - 1
        
            elif today['expectation_change'] > 0:
                today['bull_count'] += 1
                today['raw_expectations'] = yesterday['raw_expectations'] + 1

            else:
                today['raw_expectations'] = yesterday['raw_expectations']

            try:
                today['bear_bull_ratio'] = float(today['bear_count']) / float(today['bull_count'])
            except ZeroDivisionError:
                today['bear_bull_ratio'] = 0

        out.append(today)

    print(json.dumps(out, default=json_util.default, indent=2))

    f = open('Modified Data/' +ticker + '/' + ticker + '_FORMATTEDDATA.json', 'a') 
    f.write(json.dumps(out, default=json_util.default, indent=2))
    f.close()


    for data in images:
        fig, ax = plt.subplots()
        # ax.plot([x['date'] for x in instances], [x.get('index', 0) for x in instances])
        ax.plot([x['date'] for x in out], [x.get(data, 0) for x in out])

        ax.set(xlabel='Date', ylabel='Value',
                title=data)
        ax.grid()

        fig.savefig('Modified Data/' + ticker + '/' + data + ".png")

transformRawData('UVXY')
##main()

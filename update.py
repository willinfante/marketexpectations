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
import os
from io import StringIO
currentMonth = datetime.now().month

API_KEY = "api_key_here"
VALID_API_SLICES = \
  ["year1%s" % item for item in ["month%s" % i for i in range(1, 13)]] + \
  ["year2%s" % item for item in ["month%s" % i for i in range(1, 13)]]

images = ['expectation_change', 'real_change', 'index', 'bear_count', 'bull_count', 'raw_expectations', 'expectation']
mode = "TIME_SERIES_INTRADAY_EXTENDED"

def load_dates_from_csv(file_obj):
  dates = {}

  #LOOK IN DATA/SPY/SPY-TEMPORARY-UPDATE - NEED TO CHANGE CSV READ FOR DIFFERENT TYPE
  csv_reader = reader(file_obj)

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

  return dates


def name_for_slice(slice_id):
  return VALID_API_SLICES[slice_id]

def update(ticker, num_hist=1, ignore_stop_if_found=False):
  # No folder, start fresh
  if not os.path.exists('data/' + ticker):
    os.makedirs('data/' + ticker)
    current_dates = {}
  else:
    # load existing date data from datafile
    try:
      current_dates = json_util.loads(open('data/' + ticker + '/data.json', 'r').read())
      print("loaded existing %s dates from file" % len(current_dates))
    except FileNotFoundError:
      current_dates = load_dates_from_csv(open('data/' + ticker + '/data.csv', 'r'))
      print("loaded existing %s dates from file (via csv)" % len(current_dates))

  for i in range(0, num_hist):
    # this api only gives 25 months
    if i > 24:
      break

    uri = 'https://www.alphavantage.co/query?function={}&symbol={}&slice={}&interval=30min&outputsize=compact&apikey={}'.format(
      mode, ticker, VALID_API_SLICES[i], API_KEY
    )

    print("GET %s" % uri.replace(API_KEY, '$API_KEY'))

    # request most recent month of data
    res = requests.get(uri)
    lines = StringIO(res.text)

    # Load from the csv file in response
    new_dates = load_dates_from_csv(lines)
    print("loaded %s datapoints from api" % len(new_dates))

    if not new_dates:
      print("no data found in load, stopping...")
      break

    # Load the new data into the existing json list
    found_existing_data = False
    update_count = 0
    for (date_id, data) in new_dates.items():
      # if not there, add it
      if date_id not in current_dates:
        update_count += 1
        current_dates[date_id] = data
      else:
        found_existing_data = True

    # print status info
    print("added %s days to the index" % update_count)
    if not found_existing_data:
      print("warning: did not find any known endpoints, you may want to fetch historical data using --max-months-to-fetch <n> and --halt-mode=all")

    if not ignore_stop_if_found and found_existing_data:
      break

    time.sleep(5)

  print("total day count is now: %s" % len(current_dates))

  # write the inter-day data to a json file
  # this file has no algorithm crap in it.
  updated_data = json_util.dumps(current_dates, indent=2)
  f = open('data/' + ticker + '/data.json', 'w+')
  f.write(updated_data)
  f.close()

  # sort the dates for running the algorithm
  instances = list(current_dates.values())
  instances.sort(key=lambda x: x['timestamp'])

  def percent_change(initial, final):
      return (float(final) - float(initial)) / float(final)

  out = []
  yesterday = None
  for (i, today) in enumerate(instances):
      if 'closed_at' not in today and 'open_at' in today:
        today['closed_at'] = today['open_at']
      elif 'open_at' not in today and 'closed_at' in today:
        today['open_at'] = today['closed_at']
      elif 'open_at' not in today and 'closed_at' not in today:
        print('date: %s is missing data (no open / close data), skipping it.' % today['date'])
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

      yesterday = today
      out.append(today)

  output_path = 'data/' + ticker + '/output.json'
  f = open(output_path, 'w+')
  res = json.dumps(out, default=json_util.default, indent=2)
  f.write(res)
  f.close()
  print("updated %s" % output_path)

  # make images
  if not os.path.exists('data/' + ticker + '/images'):
    os.makedirs('data/' + ticker + '/images')

  # Write plots
  for data in images:
    fig, ax = plt.subplots()
    ax.plot([x['date'] for x in out], [x.get(data, 0) for x in out])
    ax.set(xlabel='Date', ylabel='Value', title='{} {}'.format(ticker, data.replace('_', ' ')))
    ax.grid()

    fig_path = 'data/' + ticker + '/images/' + data + ".png"
    fig.savefig(fig_path)
    print("updated %s" % fig_path)


if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--symbol', dest="symbol", help='the name of the symbol', default="<all>")
  parser.add_argument('--max-months-to-fetch', dest="num_hist", type=int, default=1, help='max number of months to fetch')
  parser.add_argument('--halt-mode', dest='halt_mode', help='first_known or all', default='first_known')
  args = parser.parse_args()

  if args.symbol == '<all>':
    symbols = os.listdir('data/')
  else:
    symbols = [args.symbol.strip()]

  for symbol in symbols:
    print("Updating: %s (%s months, halt mode: %s)" % (symbol, args.num_hist, args.halt_mode))
    if args.halt_mode != 'none':
      update(symbol, num_hist=args.num_hist, ignore_stop_if_found=args.halt_mode == 'all')

    f = open('data/' + symbol + '/index.html', 'w+')
    f.write("""
      <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Document</title>
        </head>
        <body>
          <h1>{symbol}</h1>
          {images}
        </body>
      </html>
    """.format(
      symbol=symbol,
      images='\n'.join(['<img src="images/%s.png">' % (image) for image in images])
    ))
  
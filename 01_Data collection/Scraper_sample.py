import datetime
import json
import os
import random
import requests
import time

data_dict = {
    'allTweets': [],
    'allIncludes': [],
    'newest_id': None,
    'oldest_id': None,
    'result_count': None, 
    'next_token': None
  }

# Configuration info: Path for saving and requested time period
directory_target = r'<enter path where you want to save the files to here>'
start = datetime.datetime(2019, 1, 1)
end = datetime.datetime(2021, 9, 13)
GUEST_ID = '<enter guest id here>'
PERS_ID = '<enter personalization id here>'

# Request Parameter
# your Twitter API v2 bearer token should be added to your env variables
BEARER_TOKEN = os.environ['BEARER_TOKEN']

payload={}
headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}', 
    'Cookie': f'guest_id={GUEST_ID}; personalization_id={PERS_ID}'
}

# Functions
# --- Create list of 12hour-step-datetimes for given time period
def create_dates(start, end):
    diff_days = (end-start).days
    return [end - datetime.timedelta(hours = x*12) for x in range(2*diff_days+1)]

# --- Randomize datetime list within 12hour windows between datetimes
def randomize_dates(dateList):
    for i in range(len(dateList)-1):
        dateList[i] = dateList[i+1] + random.random() * (dateList[i] - dateList[i+1])

    return dateList[:-1] #dont return last element -> cant be randomized within time period

# --- Scrape first page of tweets
def scrape_first(url):
  # send request to API and format as json
  response = requests.request("GET", url, headers=headers, data=payload)
  json_data = json.loads(response.text)

  # save needed data in data_dict
  try:
    data_dict['allTweets'] = list(json_data['data'])
  except KeyError:  # if no tweets are provided exit function
    data_dict['result_count'] = 0
    return

  try:  # exception needed in case no retweets are in the dataset
    data_dict['allIncludes'] = list(json_data['includes']['tweets'])
  except KeyError:
    data_dict['allIncludes'] = []

  data_dict['newest_id'] = json_data['meta']['newest_id']
  data_dict['oldest_id'] = json_data['meta']['oldest_id']
  data_dict['result_count'] = json_data['meta']['result_count']

# --- Scrape alle Tweets eines Accounts im gewählten Zeitraum
def scrape_tweets(date):
    query = 'lang:en the -the'
    url = '''https://api.twitter.com/2/tweets/search/all?
    query=query_placeholder&
    end_time=''' + date.isoformat() + '''Z&
    max_results=500&
    tweet.fields=author_id,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,public_metrics,referenced_tweets,reply_settings&
    expansions=referenced_tweets.id'''

    url = url.replace('\n', '').replace(' ', '').replace('query_placeholder', query)

    scrape_first(url)

# MAIN
# create datetime list for timeperiod
dateList = create_dates(start, end)
# randomize datetimes within 12hour windows
dateList = randomize_dates(dateList)

# scrape up to 500 tweets per 12hour windows
for date in dateList:
    time.sleep(1.1)
    scrape_tweets(date)

    # create JSON-object containung meta data about the tweet sample
    metaObject = {
        'newest_id': data_dict['newest_id'],
        'oldest_id': data_dict['oldest_id'],
        'result_count': data_dict['result_count']
    }

    # create final JSON-object containing tweets, meta data and user data
    finalObject = {
        'tweet_data': data_dict['allTweets'],
        'includes': data_dict['allIncludes'],
        'tweet_meta': metaObject
    }

    # open JSON-file and save finalObject as JSON-data
    filename = date.strftime('%Y_%m_%d_%H') + '_sample_data'
    with open(f'{directory_target}/{filename}.json', 'w+') as outfile:
        json.dump(finalObject, outfile, indent=4)

    print('🤗 Day ' + date.strftime('%Y_%m_%d_%H') + ' done, so far so good.')

print('🎉 All done, sample data collected!')
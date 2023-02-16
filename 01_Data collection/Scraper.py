import contextlib
import json
import os
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

# Configuration info: Path for saving, TUA and TUA handles
directory_target = r'<enter path where you want to save the files to here>'
accounts = ['<enter account handles you want to scrape here>']
accounts_names = ['<enter account names here - important: same order as in accounts>']
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
  
  try:  # exception needed if only one page of tweets (no next token)
    data_dict['next_token'] = json_data['meta']['next_token']
  except KeyError:
    data_dict['next_token'] = False 

# --- scrape further pages and add results to data_dict
def scrape_further(url_next):
  # send request to API and format as json
  response = requests.request("GET", url_next, headers=headers, data=payload)
  json_data = json.loads(response.text)

  # save needed data in data_dict
  try:
    for tweet in json_data['data']:
      data_dict['allTweets'].append(tweet)
  except KeyError:  # if no tweets are provided exit function
    data_dict['next_token'] = False
    return

  with contextlib.suppress(KeyError): # if no includes are provided ignore raised error and continue
    for include in json_data['includes']['tweets']:
      data_dict['allIncludes'].append(include)

  data_dict['oldest_id'] = json_data['meta']['oldest_id']
  data_dict['result_count'] += json_data['meta']['result_count']
  try:
    data_dict['next_token'] = json_data['meta']['next_token']
  except KeyError:
    data_dict['next_token'] = False

# --- Scrape all Tweets from 'accounts' within given time period
def scrape_tweets(account):
  url = '''https://api.twitter.com/2/tweets/search/all?
  query=from:''' + account + '''&
  start_time=2019-01-01T01:00:00Z&
  end_time=2021-09-13T01:00:00Z&
  max_results=500&
  tweet.fields=author_id,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,public_metrics,referenced_tweets,reply_settings
  &expansions=referenced_tweets.id'''

  url = url.replace('\n', '').replace(' ', '')

  # scrape first page of tweets (max 500 tweets)
  scrape_first(url)

  # scrape all further pages until all tweets from timeperiod are collected
  while data_dict['next_token']:
    url_next = f'{url}&next_token={data_dict["next_token"]}'

    time.sleep(1.1)

    scrape_further(url_next)

# scrape user account data
def scrape_user(account):
  url = f'https://api.twitter.com/2/users/by/username/{account}?user.fields=created_at,description,entities,location,public_metrics,url,verified'

  time.sleep(1.1)
  response = requests.request("GET", url, headers=headers, data=payload)

  return json.loads(response.text)


# Main
for account in accounts:
  filename = accounts_names[accounts.index(account)]

  scrape_tweets(account)
  
  # check if account provides tweets, if no stop scraping attempt
  if data_dict['result_count'] == 0:
    print(f'😢 Requested account {filename} has no available tweets within the timeperiod')
    time.sleep(1.1)

  else:
    user_dict = scrape_user(account)


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
        'tweet_meta': metaObject,
        'user_data': user_dict['data']
    }

    # open JSON-file and save finalObject as JSON-data
    with open(f'{directory_target}/{filename}.json', 'w+') as outfile:
      json.dump(finalObject, outfile, indent=4)

    print(f'🎉 File done: {filename}')
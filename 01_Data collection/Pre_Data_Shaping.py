import dateutil.parser as parser
import datetime
import json
from json.decoder import JSONDecodeError
import os
import re

# Variables
directory_source = r'<enter path where your tweet files are here>'
directory_target = r'<enter path where you want to save the files to here>'
counter_removed = 0     # Counter for accounts inactive during pandemic

# Functions
# --- Cycle through all tweets in dataset and return only english ones
def remove_not_english(json_data):
    counter_removed = 0

    for i in range(len(json_data['tweet_data'])):
        
        if json_data['tweet_data'][i-counter_removed]['lang'] != 'en':
            json_data['tweet_data'].pop(i-counter_removed)
            counter_removed += 1

    # Update metadata
    # --- Update newest and oldest tweet id
    json_data['tweet_meta']['newest_id'] = json_data['tweet_data'][0]['id']
    json_data['tweet_meta']['oldest_id'] = json_data['tweet_data'][len(json_data['tweet_data'])-1]['id']

    # --- Add new key for number of english/removes tweets
    json_data['tweet_meta']['result_count_english'] = len(json_data['tweet_data'])
    json_data['tweet_meta']['results_removed'] = counter_removed

    return(json_data)

# --- Check if TUA posted at least 10 tweets during pandemic
def check_activity(json_data):
    counter_duringCOVID = 0

    # Count tweets posted > 2020-01-01 UTC
    try:
        i = 0
        while parser.parse(json_data['tweet_data'][i]['created_at']) > datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc):

            counter_duringCOVID += 1

            # Exit loop if 10 tweets > 2020-01-01 UTC have been found
            if counter_duringCOVID > 9:
                break

            i += 1

    # Catch Exeption if less than 10 tweets have been posted
    except IndexError:
        counter_duringCOVID = 0

    return counter_duringCOVID > 9

# --- Expand shortened retweet text to full lenght
def full_lenght_rt(json_data):
    # Create regex object matching retweet texts and handles
    rt_re = re.compile(r'RT @([A-Za-z0-9_]+):')
    
    # Add missing retweet text from 'includes' to 'text'
    for tweet in json_data['tweet_data']:
        if re.match(rt_re, tweet['text']):
            for rt in json_data['includes']:
                try:
                    if  tweet['referenced_tweets'][0]['id'] == rt['id']:
                        tweet['text'] = tweet['text'].split(':')[0] + ': ' + rt['text']
                        break
                except KeyError:
                    break
    
    json_data.pop('includes')
    return (json_data)

# MAIN - prepare file for jupyter analysis
for filename in os.listdir(directory_source):

    try:

        with open(f'{directory_source}/{filename}', encoding='utf8') as json_file:   # open with UTF-8 encoding for emojis
            try:
                json_data = json.load(json_file)

                # Remove non-english tweets from dataset
                json_data = remove_not_english(json_data)

                # Check if TUA posted at least 10 tweets since Jan 2020
                active = check_activity(json_data)
                # --- If not enough Tweets dont save TUA for further analysis
                if not active:
                    counter_removed += 1
                    print(f'😥 File removed due to lack of Tweets during COVID: {filename}')
                    continue

                # Check if TUA has at least 1000 followers
                if json_data['user_data']['public_metrics']['followers_count'] < 1000:
                    counter_removed += 1
                    print(f'😥 File removed due to lack of Followers: {filename}')
                    continue

                # Complete shortened retweets via 'includes'
                json_data = full_lenght_rt(json_data)

            except JSONDecodeError:
                print('Some weird error, this really should not happen... yay?')
                print(f'File with error: {directory_source}/{filename}')

        # open JSON-file and save JSON data to it
        with open(f'{directory_target}/{filename}', 'w+') as outfile:
            json.dump(json_data, outfile, indent=4)

        print(f'🎉 File done: {filename}')

    except FileNotFoundError:
        print(f'No file found in location: {directory_source}/{filename}')
# Twitter_Religion-Resilience
This repository features code from the research project "Digital Religious Communication and the Facilitation of Resilient Faith: A Study of the Twitter Activity of Ecumenical and Social Justice-Oriented Groups during the COVID-19 Pandemic" to replicate the results or adapt to your own study

## This project consists of...
The project provides code according to the study mentioned above. This includes 
1. python-scripts for data-collection and pre-cleaning
2. jupyter notebooks for data cleaning
3. jupyter notebooks for the statistical analysis conducted (communication volume & sentiment)
4. jupyter notebooks for the topic modeling conducted

Additionally, the datasets used for the study can be requested via the project owner.

## Remarks for using the code
### Twitter API v2
The data collection using the python files is based on access to Twitter's academic research API. Access can be requested via 'https://developer.twitter.com/en/products/twitter-api/academic-research'. Once access is granted a token will be provided by Twitter. The token has to be saved as environment variable - the according variable's name then must be 'Scraper.py' and 'Scraper_sample.py' 

### Credits
Credit for the randomization approach in 'Scraper_sample' is due to the following post:https://twittercommunity.com/t/generating-a-random-set-of-tweet-ids/150255.
Also, the topic analysis and the hyperparameter adjustment were based on the paper "Twitter Topic Modeling" by Amin Azad (Azad, Amin, 2020. ‘GitHub: some-labs-24 / data-science’. https://github.com/some-labs-24/data-science).




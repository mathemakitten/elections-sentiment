# 2019 Canadian Federal Elections Sentiment 
This is an analysis of the 2019 Canadian election, as told by the ongoing Twitter conversation.

**Election date:**  October 21

**Twitter queries**

Tweets are counted in this dataset if they use an official election hashtag, 
or are tweeted by an official party leader.

`QUERY = '#cdnpoli OR #elxn43 OR #polcan OR #ItsOurVote OR #CestNotreVote OR from:justintrudeau OR from:AndrewScheer OR from:ElizabethMay OR from:theJagmeetSingh OR from:MaximeBernier OR from:yfblanchet'`

## Dataset
* 180 days (6 months) of data from Twitter from March 29 - September 25 2019 (11am), 
one month leading up to the election 
* No other constraints (i.e. min_faves, retweets, geo, etc.)
* Tweets can be in English or French (or any other language)
* Twitter has stated that [there has not been any wide-scale disinformation](https://globalnews.ca/news/5943227/canada-election-twitter-manipulation/) 
campaigns on the election as of September 24 2019
* It takes ~7 minutes to scrape a day's worth of tweets (25k tweets),
7 * 180 minutes = 21 hours (+30 seconds for sleep, lol)
* As of end of September, ~900k (Oct 3: 983588) tweets with 15 columns: `'username', 'to', 'text', 'retweets', 'favorites', 'replies', 'id',
       'permalink', 'author_id', 'date', 'formatted_date', 'mentions',
       'hashtags', 'geo', 'urls'`
       
## Methodology
* The dashboard is built with Plotly + Dash, and (will be) hosted on Google App Engine
* Tweets are encoded with Universal Sentence Encoder after tokenization with
the NLTK `TweetTokenizer`

## Limitations
*  Twitter data needs to be re-scraped every few days because favorites & retweets are monotonically 
increasing over time. It currently takes 24-36 hours to scrape March 29 - today.
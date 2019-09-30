# 2 days of tweets = 25k and then cut off, so need to scrape day-by-day and parse

import GetOldTweets3 as got
import datetime
import time
from get_tweets import _get_tweet_object, _convert_tweets_to_dataframe
from utils import get_logger

logger = get_logger('Scrape')
#now = datetime.datetime.now()

# TODAY = datetime.datetime.today() # USE THIS IF SCRAPING FROM TODAY OTHERWISE USE LINE BELOW
TODAY = datetime.datetime.strptime('2019-04-10', '%Y-%m-%d')  # prev Sept 25
MIN_DATE = datetime.datetime.strptime('2019-03-29', '%Y-%m-%d')
#date_list = [TODAY - datetime.timedelta(days=x) for x in range(NUM_DAYS)]
date_list = [TODAY - datetime.timedelta(days=x) for x in range((TODAY-MIN_DATE).days + 1)]

for date in date_list:
    time.sleep(15)
    NEXT_DAY = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    DATE = date.strftime("%Y-%m-%d")
    logger.info("Scraping tweets for {}".format(date))
    #QUERY = "#cdnpoli OR #elxn43 OR #polcan OR #ItsOurVote OR #CestNotreVote" # --since {} --until {}".format(date, date)
    QUERY = 'from:justintrudeau' # justintrudeau AndrewScheer ElizabethMay theJagmeetSingh MaximeBernier yfblanchet

    tweet_criteria = got.manager.TweetCriteria().setQuerySearch(QUERY).setSince(DATE).setUntil(NEXT_DAY)
    #tweet_criteria = _create_search_criteria(QUERY, date, date, -1)
    tweets = _get_tweet_object(tweet_criteria)
    df = _convert_tweets_to_dataframe(tweets)

    logger.info("Done scraping tweets for {}".format(date))

    df.to_csv('tweets/cdnpoli_{}.csv'.format(date.strftime("%Y%m%d")), index=False)
    logger.info("Successfully saved tweets for {}".format(DATE))

logger.info("Completed tweet scraping for {} until {}".format(date_list[-1].strftime("%Y-%m-%d"), date_list[0].strftime("%Y-%m-%d")))


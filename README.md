# elections-sentiment
analysis of sentiment on the 2019 Canadian election

**Twitter queries**
```
(#cdnpoli, OR #elxn43, OR #polcan, OR #ItsOurVote, OR #CestNotreVote)

GetOldTweets3 --querysearch "(#cdnpoli, OR #elxn43, OR #polcan, OR #ItsOurVote, OR #CestNotreVote) --since 2019-09-20 --until 2019-09-24" --maxtweets 1000
```

## Dataset
* **Canadian federal election:** October 21, 2019
* 180 days (6 months) of data from Twitter from March 29 - September 25 2019 (11am), 
one month leading up to the election 
* Tweets must contain one of the official elections hashtags `#cdnpoli, OR #elxn43, OR #polcan, OR #ItsOurVote, OR #CestNotreVote`
* No other constraints (i.e. min_faves, retweets, geo, etc.)
* Twitter has stated that [there has not been any wide-scale disinformation](https://globalnews.ca/news/5943227/canada-election-twitter-manipulation/) 
campaigns on the election as of September 24 2019
* It takes ~3.5 minutes to scrape a day's worth of tweets (25k tweets)

## Questions 
* Do we need to clean the tweets data, or should we leave it as-is for encoding? 
(i.e. clean links, hashtags, @replies)

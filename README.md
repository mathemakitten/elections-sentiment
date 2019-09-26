# 2019 Canadian Federal Elections Sentiment 
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
* Tweets can be in English or French (or any other language)
* Twitter has stated that [there has not been any wide-scale disinformation](https://globalnews.ca/news/5943227/canada-election-twitter-manipulation/) 
campaigns on the election as of September 24 2019
* It takes ~7 minutes to scrape a day's worth of tweets (25k tweets),
7 * 180 minutes = 21 hours (+30 seconds for sleep, lol)
* 899,555 tweets with 15 columns: `'username', 'to', 'text', 'retweets', 'favorites', 'replies', 'id',
       'permalink', 'author_id', 'date', 'formatted_date', 'mentions',
       'hashtags', 'geo', 'urls'`

## Questions 
* Do we need to clean the tweets data, or should we leave it as-is for encoding? 
(i.e. clean links, hashtags, @replies)
* How many clusters should we have? Does this number change over time?  
* Do we need to split out the analysis week-by-week? 
(i.e. here's what's trending in Canadian politics this week)
-- might depend on how different is 

## TODO 
* [x] Scrape 180 days of Canadian political Twitter data
* [ ] Build some graphs
    * [x] Count of tweets over time (hypothesis: more people start tweeting closer to the election)
    * [ ] Map out most popular hashtags over time 
    * [ ] Map out most popular words over time
* [ ] Encode all tweets with Universal Sentence Encoder
* [ ] Run unsupervised methods on it 
* [ ] Graph relative size of each cluster
* [ ] Try the Tensorflow [Multilingual Universal Sentence Encoder for Semantic Retrieval](https://tfhub.dev/s?q=universal-sentence-encoder-multilingual) 
to identify tweets which are semantically similar
    * Can we use this to identify disinformation?
    
## Data notes to look into 
* Sept 22nd dataset seems to only have 3740 tweets and the min_date is `'2019-09-22 18:00:43+00:00'`
-- why is this? 
* Sept 21 and 23 seem to be OK though

## Data scraping progress 
* March 29 - September 25 completed 
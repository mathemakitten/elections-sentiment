# python get_tweets.py -q 'datacamp' -ts '2019-03-01' -tu '2019-05-01'

# Starbucks search: -from:Starbucks (@Starbucks) until:2018-04-20 since:2018-04-10 exclude:replies
# GetOldTweets3 --querysearch "-from:Starbucks (@Starbucks) until:2018-04-20 since:2018-04-10 exclude:replies -filter:nativeretweets min_faves:10"
# -from:chickfila ("toronto" AND "chick-fil-a") OR ("toronto" AND to:chickfila) since:2019-01-01
import os
import re
import time
from pprint import pformat
import datetime

import pandas as pd
import GetOldTweets3 as got

from utils import load_csv, Timer, paths

USE_TWEETS_COLS = ['username', 'formatted_date', 'cleaned_text', 'text']

PRE_PROCESSING_OPTIONS = {
    # custom
    'lower_string': True,
    'remove_url': True,
    'remove_at_string': True,

    # gensim
    'remove_stopwords': True,
    'split_alphanum': False,
    'stem_text': False,
    'strip_non_alphanum': False,
    'strip_punctuation': True,
    'strip_tags': True,
    'strip_numeric': True,
    'strip_multiple_whitespaces': True,
}


def create_preprocessing_functions(pre_processing_options):
    import gensim.parsing.preprocessing as p
    import preprocessor

    pre_processing_options_str_formatted = pformat(pre_processing_options, indent=2)
    #print('Preprocessing tweet text with following choices:\n{}\n'.format(pre_processing_options_str_formatted))

    # remove URL and emoji and simple smiley
    preprocessor.set_options(preprocessor.OPT.URL, preprocessor.OPT.EMOJI,
                             preprocessor.OPT.SMILEY)

    pre_processing_funcs = {
        # custom
        'lower_string': lambda s: s.lower(),
        'remove_url': preprocessor.clean,
        'remove_at_string': lambda s: re.sub(r'@\w+', '', s),

        # gensim
        'remove_stopwords': p.remove_stopwords,
        'split_alphanum': p.split_alphanum,
        'stem_text': p.stem_text,
        'strip_non_alphanum': p.strip_non_alphanum,
        'strip_numeric': p.strip_numeric,
        'strip_punctuation': p.strip_punctuation,
        'strip_tags': p.strip_tags,
        'strip_multiple_whitespaces': p.strip_multiple_whitespaces,
    }

    use_preprocessing_funcs = []
    for k, v in pre_processing_options.items():
        if v:
            use_preprocessing_funcs.append(pre_processing_funcs[k])

    patch = lambda s: re.sub(r'(“|”|’)', '', s)
    use_preprocessing_funcs.append(patch)

    def _preprocessing_func(s):
        s_processed = s
        for f in use_preprocessing_funcs:
            s_processed = f(s_processed)
        return s_processed

    return _preprocessing_func


def get_cleaned_tweets(query_dict):
    """
    Get cleaned tweets
    :param query_dict:
        query_string: 'datacamp lang:en'
        time_since: '2019-03-01'
        time_until: '2019-05-01'
        max_tweets: 0 for unlimited
    :return: dataframe
    """

    file_name = _convert_query_dict_to_str_as_filename(query_dict)
    save_cleaned_file_name = paths.cleaned_tweets / 'cleaned_{}.csv'.format(file_name)

    if save_cleaned_file_name.is_file():
        print('Cleaned file {} already exists, reload'.format(save_cleaned_file_name))
        tweet_df = load_csv(save_cleaned_file_name)
    else:
        tweet_df = get_raw_tweets(query_dict)

        print('Cleaning tweets')
        cleaned_tweet_df = _clean_tweets_text(tweet_df)

        #print('Select only {USE_TWEETS_COLS} and save tweets to: {repr(save_cleaned_file_name)}'.format())
        cleaned_tweet_df[USE_TWEETS_COLS].to_csv(save_cleaned_file_name, index=False)

    print('Done getting tweets.')
    return tweet_df


def get_raw_tweets(query_dict):
    """
    Get raw tweets
    :param query_dict:
        query_string: 'datacamp lang:en'
        time_since: '2019-03-01'
        time_until: '2019-05-01'
        max_tweets: 0 for unlimited
    :return: dataframe
    """
    file_name = _convert_query_dict_to_str_as_filename(query_dict)
    save_raw_file_name = paths.raw_tweets / 'raw_{}.csv'.format(file_name)

    if save_raw_file_name.is_file():
        print('Raw file {} already exists, reload'.format(repr(save_raw_file_name)))
        tweet_df = load_csv(save_raw_file_name)
    else:
        _validate_query(query_dict)

        print(f'Getting raw tweets with query:\n{query_dict!r}')
        tweet_criteria = _create_search_criteria(**query_dict)
        tweet_objects = _get_tweet_object(tweet_criteria)
        tweet_df = _convert_tweets_to_dataframe(tweet_objects)

        print(f'Saving raw tweets to: {repr(save_raw_file_name)}')
        tweet_df.to_csv(save_raw_file_name, index=False)

    print('Done getting raw tweets.')
    return tweet_df


def remove_tweets_by_user(tweets, user):
    print(f'Removing user: {repr(user)}, original input length: {len(tweets):,}')
    _tweets = tweets.copy()
    _tweets['username'] = _tweets['username'].str.lower()
    _tweets = _tweets[_tweets['username'] != user.lower()].reset_index(drop=True)
    print(f'Done removing {repr(user)}, length now is: {len(_tweets):,}')
    return _tweets


def _convert_query_dict_to_str_as_filename(query_dict):
    query_str_formatted = '_'.join([str(v).replace(' ', '_') for v in query_dict.values()])
    return query_str_formatted


def _validate_query(query_dict):
    required_keys = ('query_string', 'time_since', 'time_until', 'max_tweets')
    if all(k in query_dict for k in required_keys):
        print('(All required query arguments are provided)')
    else:
        raise ValueError(f'{query_dict} does not have all required keys')


def _create_search_criteria(query_string, time_since, time_until, max_tweets):
    """
    query_string: 'datacamp lang:en'
    since: '2019-03-01'
    until: '2019-05-01'
    max_tweets: 0 for unlimited
    """
    tweetCriteria = (got.manager.TweetCriteria().setQuerySearch(f'{query_string} lang:en')
                     .setSince(time_since)
                     .setUntil(time_until)
                     .setMaxTweets(max_tweets))
    return tweetCriteria


def _get_tweet_object(tweet_criteria):
    with Timer('Get tweets'):
        current_time = datetime.datetime.now().replace(microsecond=0)
        print(f'Start tweet query at: {current_time}')
        tweets = got.manager.TweetManager.getTweets(tweet_criteria)
        print(f'Done query, {len(tweets):,} tweets returned')
    return tweets


# def _get_tweet_object(tweet_criteria):
#     import signal
#
#     def _handler(signum, frame):
#         print("tweets took too long to retrieve!")
#         raise Exception("end of querying, return empty tweets")
#
#     signal.signal(signal.SIGALRM, _handler)
#     timeout = 15 * 60  # 15 mins
#     signal.alarm(timeout)
#
#     with Timer('Get tweets'):
#         try:
#             current_time = datetime.datetime.now().replace(microsecond=0)
#             print(f'Start tweet query at: {current_time}')
#             tweets = got.manager.TweetManager.getTweets(tweet_criteria)
#             print(f'Done query, {len(tweets):,} tweets returned')
#         except Exception as exc:
#             print(exc)
#             tweets = ''
#     return tweets


def _convert_tweets_to_dataframe(tweets):
    """
    tweets: list of tweet object
    """
    pd.options.display.max_colwidth = 100
    data = [vars(t) for t in tweets]
    df = pd.DataFrame.from_records(data)
    return df


def _clean_tweets_text(tweet_df):
    with Timer('clean tweets text'):
        processing_func = create_preprocessing_functions(PRE_PROCESSING_OPTIONS)
        tweet_df['cleaned_text'] = tweet_df['text'].apply(processing_func)

        empty_str_after_cleaning = (tweet_df['cleaned_text'].isna()) | (tweet_df['cleaned_text'] == '')
        num_empty_str_after_cleaning = empty_str_after_cleaning.sum()
        print(f'There are {num_empty_str_after_cleaning:,} number of empty text after cleaning, dropping them')
        tweet_df = tweet_df[~empty_str_after_cleaning].reset_index(drop=True)
    return tweet_df


def _select_only_used_columns(tweet_df, use_cols):
    return tweet_df[use_cols]


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get raw/clean tweets')
    parser.add_argument('-q', '--query-string', type=str, default='datacamp lang:en')
    parser.add_argument('-ts', '--time-since', type=str, default='2019-03-01')
    parser.add_argument('-tu', '--time-until', type=str, default='2019-05-01')
    parser.add_argument('-n', '--max-tweets', type=int, nargs='?', const=0, default=0)
    args = parser.parse_args()

    tweet_df = get_cleaned_tweets(query_dict=vars(args))
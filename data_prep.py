import glob
import pandas as pd
from collections import Counter
import datetime
import os
import pickle

# Constants
day_of_week_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
color_dict = {'AndrewScheer': '#1A4782', 'JustinTrudeau': '#D71920', 'theJagmeetSingh': '#F37021', 'ElizabethMay': '#3D9B35', 'yfblanchet': '#33B2CC'}
LEADER_USERNAMES = ['JustinTrudeau', 'AndrewScheer', 'ElizabethMay', 'theJagmeetSingh', 'yfblanchet']
hour_dict = {'00': 'Midnight', '01': '1:00 AM', '02': '2:00 AM', '03': '3:00 AM', '04': '4:00 AM', '05': '5:00 AM', '06': '6:00 AM',
             '07': '7:00 AM', '08': '8:00 AM', '09': '9:00 AM', '10': '10:00 AM', '11': '11:00 AM', '12': '12:00 PM',
             '13': '1:00 PM', '14': '2:00 PM', '15': '3:00 PM', '16': '4:00 PM', '17': '5:00 PM', '18': '6:00 PM',
             '19': '7:00 PM', '20': '8:00 PM', '21': '9:00 PM', '22': '10:00 PM', '23': '11:00 PM'}

# TODO CACHE ALL OF THESE

def load_and_clean_data():

    THIS_FILE = 'cache/df.pkl'

    if not os.path.isfile(THIS_FILE):
        files = glob.glob('tweets/cdnpoli_*.csv') #[0:30] #TODO get rid of this sample
        df = pd.read_csv(files[0])

        for file in files[1:]:
            df_tmp = pd.read_csv(file)
            df = pd.concat([df, df_tmp])

        df['day'] = pd.to_datetime(df['date']).dt.date
        df['day_of_week'] = [x.weekday() for x in df['day']]
        df.replace({'day_of_week': day_of_week_mapping})

        pickle.dump(df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        df = pickle.load(open(THIS_FILE, 'rb'))
    return df


def data_prep_calculate_tweet_volume(df):

    THIS_FILE = 'cache/tweet_volume_df.pkl'

    if not os.path.isfile(THIS_FILE):
        tweet_volume_df = pd.DataFrame(data={'num_tweets': df['day'].value_counts().sort_index(),
                                             'day_of_week': pd.to_datetime(df['day'].value_counts().sort_index().index).dayofweek.map(day_of_week_mapping)},
                                       index=df['day'].value_counts().sort_index().index)
        pickle.dump(tweet_volume_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        tweet_volume_df = pickle.load(open(THIS_FILE, 'rb'))
    return tweet_volume_df


def data_prep_retweet_df(df):

    THIS_FILE = 'cache/retweet_df.pkl'

    if not os.path.isfile(THIS_FILE):
        retweet_df = df.sort_values(by=['retweets'], ascending=False)[['username', 'day', 'text', 'retweets']].head(10)
        pickle.dump(retweet_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        retweet_df = pickle.load(open(THIS_FILE, 'rb'))
    return retweet_df


def data_prep_favorites_df(df):

    # Note: decided not to cache this because I suspect it's faster to run this in-memory than load from disk?
    return df.sort_values(by=['favorites'], ascending=False)[['username', 'day', 'text', 'favorites']].head(10)


def data_prep_top10_mentions(df):

    THIS_FILE = 'cache/mentions_df.pkl'

    if not os.path.isfile(THIS_FILE):
        all_mentions = df['mentions'].str.cat(sep=' ').split(' ')
        mentions_df = pd.DataFrame(Counter(all_mentions).most_common(10), columns=['mentions', 'count'])
        pickle.dump(mentions_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        mentions_df = pickle.load(open(THIS_FILE, 'rb'))
    return mentions_df


def data_prep_top10_accounts_fave(df):

    THIS_FILE = 'cache/top10_accounts_faves_df.pkl'

    if not os.path.isfile(THIS_FILE):
        top10_accounts_faves_df = df.groupby(['username']).agg({'favorites': sum}).sort_values('favorites', ascending=False).head(10)
        pickle.dump(top10_accounts_faves_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        top10_accounts_faves_df = pickle.load(open(THIS_FILE, 'rb'))

    return top10_accounts_faves_df


def data_prep_top10_accounts_retweets(df):

    THIS_FILE = 'cache/top10_accounts_retweets_df.pkl'

    if not os.path.isfile(THIS_FILE):
        top10_accounts_retweets_df = df.groupby(['username']).agg({'retweets': sum}).sort_values('retweets', ascending=False).head(10)
        pickle.dump(top10_accounts_retweets_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        top10_accounts_retweets_df = pickle.load(open(THIS_FILE, 'rb'))

    return top10_accounts_retweets_df


def data_prep_hashtag_counts_df(df):

    THIS_FILE = 'cache/hashtag_counts_df.pkl'

    if not os.path.isfile(THIS_FILE):
        all_hashtags = df['hashtags'].str.cat(sep=' ').split(' ')
        hashtag_counts_df = pd.DataFrame(Counter(all_hashtags).most_common(25), columns=['hashtag', 'count'])
        pickle.dump(hashtag_counts_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        hashtag_counts_df = pickle.load(open(THIS_FILE, 'rb'))
    return hashtag_counts_df


def data_prep_tweets_by_time(df):

    THIS_FILE = 'cache/average_number_of_tweets_per_hour.pkl'

    if not os.path.isfile(THIS_FILE):
        df['date'] = pd.to_datetime(df['date'])
        df['hour'] = df['date'].dt.strftime('%H')
        average_number_of_tweets_per_hour = df.groupby(['hour'])['hour'].count() / df['day'].nunique()
        pickle.dump(average_number_of_tweets_per_hour, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        average_number_of_tweets_per_hour = pickle.load(open(THIS_FILE, 'rb'))
    return average_number_of_tweets_per_hour


def data_prep_links_df(df):
    # TODO: cache this, maybe (needs to return 2 things)
    links_to_keep = []
    all_urls = df['urls'].str.cat(sep=' ').split(' ')
    for link in all_urls:
        if 'twitter' not in link:
            links_to_keep.append(link)
    links_df = pd.DataFrame(Counter(links_to_keep).most_common(10), columns=['link', 'count'])
    return links_df, all_urls


def data_prep_domains_df(all_urls):

    THIS_FILE = 'cache/domains_df.pkl'

    if not os.path.isfile(THIS_FILE):
        from urllib.parse import urlparse
        domains = []
        for link in all_urls:
            if all(x not in link for x in ['twitter', 'bit.ly', 'ow.ly']):
                domains.append(urlparse(link).netloc)
        domains_df = pd.DataFrame(Counter(domains).most_common(10), columns=['domain', 'count'])
        pickle.dump(domains_df, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        domains_df = pickle.load(open(THIS_FILE, 'rb'))
    return domains_df


def data_prep_leader_df(df):
    leader_df = df[df['username'].isin(LEADER_USERNAMES)]
    leader_df['days_until_election'] = [(x - datetime.date(2019, 10, 21)).days for x in pd.to_datetime(leader_df['day']).dt.date]
    return leader_df


def data_prep_count_hashtags_by_leader(df):

    THIS_FILE = 'cache/leader_hashtag_counts.pkl'

    if not os.path.isfile(THIS_FILE):
        leader_hashtag_counts = {}
        for leader in LEADER_USERNAMES:
            leader_hashtags = df[df['username'] == leader]['hashtags'].str.cat(sep=' ').split(' ')
            leader_hashtag_counts_df = pd.DataFrame(Counter(leader_hashtags).most_common(10), columns=['hashtag', 'count'])
            leader_hashtag_counts[leader] = leader_hashtag_counts_df
        pickle.dump(leader_hashtag_counts, open(THIS_FILE, 'wb'))
    else:
        print("Loading {} from cache".format(THIS_FILE))
        leader_hashtag_counts = pickle.load(open(THIS_FILE, 'rb'))
    return leader_hashtag_counts

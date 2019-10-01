import glob
import pandas as pd
from collections import Counter

# Constants
day_of_week_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
color_dict = {'AndrewScheer': '#1A4782', 'JustinTrudeau': '#D71920', 'theJagmeetSingh': '#F37021', 'ElizabethMay': '#3D9B35', 'yfblanchet': '#33B2CC'}

def load_and_clean_data():
    files = glob.glob('tweets/cdnpoli_*.csv')[0:30] #TODO get rid of this sample
    df = pd.read_csv(files[0])

    for file in files[1:]:
        df_tmp = pd.read_csv(file)
        df = pd.concat([df, df_tmp])

    df['day'] = pd.to_datetime(df['date']).dt.date
    df['day_of_week'] = [x.weekday() for x in df['day']]
    df.replace({'day_of_week': day_of_week_mapping})

    return df


def data_prep_retweet_df(df):
    retweet_df = df.sort_values(by=['retweets'], ascending=False)[['username', 'day', 'text', 'retweets']].head(10)
    return retweet_df


def data_prep_favorites_df(df):
    return df.sort_values(by=['favorites'], ascending=False)[['username', 'day', 'text', 'favorites']].head(10)


def data_prep_hashtag_counts_df(df):
    all_hashtags = df['hashtags'].str.cat(sep=' ').split(' ')
    hashtag_counts_df = pd.DataFrame(Counter(all_hashtags).most_common(25), columns=['hashtag', 'count'])
    return hashtag_counts_df


def data_prep_links_df(df):
    links_to_keep = []
    all_urls = df['urls'].str.cat(sep=' ').split(' ')
    for link in all_urls:
        if 'twitter' not in link:
            links_to_keep.append(link)
    links_df = pd.DataFrame(Counter(links_to_keep).most_common(10), columns=['link', 'count'])
    return links_df, all_urls


def data_prep_domains_df(all_urls):
    from urllib.parse import urlparse
    domains = []
    for link in all_urls:
        if all(x not in link for x in ['twitter', 'bit.ly', 'ow.ly']):
            domains.append(urlparse(link).netloc)
    domains_df = pd.DataFrame(Counter(domains).most_common(10), columns=['domain', 'count'])
    return domains_df


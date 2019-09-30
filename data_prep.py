import glob
import pandas as pd

# Constants
day_of_week_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

def load_and_clean_data():
    files = glob.glob('tweets/cdnpoli_*.csv')[0:30] #TODO get rid of this sample
    df = pd.read_csv(files[0])

    for file in files[1:]:
        df_tmp = pd.read_csv(file)
        df = pd.concat([df, df_tmp])

    df['day'] = pd.to_datetime(df['date']).dt.date
    df['day_of_week'] = [x.weekday() for x in df['day']]
    df.replace({'day_of_week': day_of_week_mapping})


def data_prep_retweet_df(df):
    retweet_df = df.sort_values(by=['retweets'], ascending=False)[['username', 'day', 'text', 'retweets']].head(10)
    return retweet_df
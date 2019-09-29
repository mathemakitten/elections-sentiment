# This is a replacement for cluster-tweets-unsupervised.ipynb, which kept disconnecting due to network issues

import tensorflow as tf
import glob
import pandas as pd
import numpy as np
import seaborn as sns
from utils import get_logger, check_gpu
from sklearn.cluster import KMeans

import tensorflow_hub as hub
import tensorflow as tf
import random

import pickle
import os

logger = get_logger("LOGGER")


def split_sentences(claims_list, n):
    for i in range(0, len(claims_list), n):
        if i % 100000 == 0:
            logger.info("Currently sentence {} of {}".format(i, len(claims_list)))
        yield claims_list[i:i+n]


def embed_tweets(tweets_to_encode):
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        tweets_embeddings = session.run(tf_hub_embedder(tweets_to_encode))

    return tweets_embeddings


def plot_similarity(labels, features, rotation):
    print("Calculating inner product of embedding vectors")
    corr = np.inner(features, features)
    print("Plotting...")
    sns.set(font_scale=1.2)
    g = sns.heatmap(
      corr,
      xticklabels=labels,
      yticklabels=labels,
      vmin=0,
      vmax=1,
      cmap="YlOrRd")
    g.set_xticklabels(labels, rotation=rotation)
    g.set_title("Semantic Textual Similarity")

check_gpu()

module_url = 'https://tfhub.dev/google/universal-sentence-encoder/2'
tf_hub_embedder = hub.Module(module_url)

# Hyperparameter search for number of clusters for k-means
n_clusters = [5, 10, 12, 14, 16]
clustering_method = 'kmeans'

logger.info("Loading data")
files = glob.glob('tweets/cdnpoli_*.csv')
df = pd.read_csv(files[0])

for file in files[1:]:
    df_tmp = pd.read_csv(file)
    df = pd.concat([df, df_tmp])

# Add a date column without timestamps
df['day'] = pd.to_datetime(df['date']).dt.date

logger.info("Data successfully loaded")
#df = df.head(100) # TODO REMOVE THIS!!!

# Tokenize tweets with the Stanford PTB tokenizer
'''
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

# Add the jar and model via their path (instead of setting environment variables):
jar = 'your_path/stanford-postagger-full-2016-10-31/stanford-postagger.jar'
model = 'your_path/stanford-postagger-full-2016-10-31/models/english-left3words-distsim.tagger'

pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')

text = pos_tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))
print(text)
'''
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
#
# import os
# os.environ['JAVAHOME'] = '/usr/bin/java'
#
# # Add the jar and model via their path (instead of setting environment variables):
# jar = 'stanford-postagger-2018-10-16/stanford-postagger-3.9.2.jar'
# model = 'stanford-postagger-2018-10-16/models/english-left3words-distsim.tagger'
# pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')


if not os.path.isfile('cache/all_tweets_embedded.pkl'):
    logger.info("Running sentence embedding")
    from nltk.parse.corenlp import CoreNLPParser
    st = CoreNLPParser()
    # TODO finish correct tokenization

    logger.info("Splitting sentences into batches")
    tweets_to_embed = list(df['text'])
    tweets_to_embed = [st.tokenize((tweet)) for tweet in tweets_to_embed]
    sentences_batched = list(split_sentences(tweets_to_embed, 200000))
    logger.info("Done batching tweets")

    all_tweets_embedded = []

    logger.info("Embedding tweets")
    for i, tweet_batch in enumerate(sentences_batched):
        logger.info("Batch {} of {}".format(i, len(sentences_batched)))
        tweets_embedding = embed_tweets([str(tweet) for tweet in tweet_batch])
        all_tweets_embedded.extend(tweets_embedding)
    pickle.dump(all_tweets_embedded, open('cache/all_tweets_embedded.pkl', 'wb'))
else:
    logger.info("Loaded embedded tweets from cache")
    all_tweets_embedded = pickle.load(open('cache/all_tweets_embedded.pkl', 'rb'))

# TODO try other clustering techniques
# logger.info("Clustering method: {}".format(clustering_method))
# for i, n in enumerate(n_clusters):
#     logger.info("Clustering attempt {} of {}".format(i, len(n_clusters)))
#     kmeans = KMeans(n_clusters=n, random_state=0).fit(all_tweets_embedded)
#
#     predictions = kmeans.predict(all_tweets_embedded)
#     df['cluster'] = predictions
#
#     # Save dataframe for exploration in a notebook
#     df.to_csv('tmp/clustering_attempt_{}_{}clusters.csv'.format(clustering_method, n))

n=10
kmeans = KMeans(n_clusters=n, random_state=0).fit(all_tweets_embedded)
predictions = kmeans.predict(all_tweets_embedded)
df['cluster'] = predictions
df.to_csv('tmp/clustering_attempt_{}_{}clusters.csv'.format(clustering_method, n))


# Look at samples from the cluster
# random.sample(list(df[df['cluster'] == 0]['text']), 10)
logger.info("Done")


# Top 50 hashtags
import plotly.express as px
from collections import Counter
all_hashtags = df['hashtags'].str.cat(sep=' ').split(' ')
hashtag_counts = pd.DataFrame(Counter(all_hashtags).most_common(50), columns=['hashtag', 'count'])
top10_hashtags = html.Div(children=[
    dcc.Graph(
        id='top10_hashtags',
        figure=go.Figure(data=go.Bar(y=hashtag_counts['count'],
                                     x=hashtag_counts['hashtag']),
                         layout=go.Layout(title='Top 10 Accounts by Favourites',
                                                hovermode='closest',
                                                xaxis={'title': 'times tweets favourited by others'},
                                                yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                          )),
    ),
    html.Span(children=[html.P('This graph aims to capture tweeters by tweet volume.')], style={'text-align': 'center'})
], className="six columns")

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
n_clusters = 5

files = glob.glob('tweets/cdnpoli_*.csv')
df = pd.read_csv(files[0])

for file in files[1:]:
    df_tmp = pd.read_csv(file)
    df = pd.concat([df, df_tmp])

# Add a date column without timestamps
df['day'] = pd.to_datetime(df['date']).dt.date

df = df.head(100) # TODO REMOVE THIS!!!

logger.info("Splitting sentences into batches")
tweets_to_embed = list(df['text'])
sentences_batched = list(split_sentences(tweets_to_embed, 200000))
logger.info("Done batching tweets")

all_tweets_embedded = []

logger.info("Embedding tweets")
for i, tweet_batch in enumerate(sentences_batched):
    logger.info("Batch {} of {}".format(i, len(sentences_batched)))
    tweets_embedding = embed_tweets([str(tweet) for tweet in tweet_batch])
    all_tweets_embedded.extend(tweets_embedding)

kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(all_tweets_embedded)
predictions = kmeans.predict(all_tweets_embedded)
df['cluster'] = predictions

logger.info("Done")


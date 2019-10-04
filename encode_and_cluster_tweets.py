import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import glob
import pandas as pd
import numpy as np
import seaborn as sns
from utils import get_logger, check_gpu
from sklearn.cluster import KMeans

import tensorflow_hub as hub
import tensorflow as tf

import pickle
import os

from nltk.tokenize import TweetTokenizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
import umap
import nltk

logger = get_logger("LOGGER")

from nltk.tag import StanfordPOSTagger
# Add the jar and model via their path (instead of setting environment variables):
jar = 'stanford-postagger-2018-10-16/stanford-postagger-3.9.2.jar'
model = 'stanford-postagger-2018-10-16/models/english-left3words-distsim.tagger'
pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')


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

# module_url = 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/1'
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

if not os.path.isfile('cache/all_tweets_embedded.pkl'):
    logger.info("Running sentence embedding")
    os.environ['CLASSPATH'] = 'stanford-postagger-2018-10-16'

    logger.info("Tokenizing with NLTK's TweetTokenizer")
    # TODO figure out how much of this will be poor performance due to the French
    detokenizer = TreebankWordDetokenizer()
    tweet_tokenizer = TweetTokenizer(preserve_case=False, strip_handles=False, reduce_len=False)
    df['text_clean'] = [detokenizer.detokenize(tweet_tokenizer.tokenize(str(tweet))) for tweet in df['text']]

    # logger.info("Splitting sentences into batches")
    tweets_to_embed = list(df['text_clean'])
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
#


# TODO kill this -- k means takes forever and likely won't work on 512 dimensions
n=50
logger.info("Running k-means")
kmeans = KMeans(n_clusters=n, random_state=0, verbose=1, n_jobs=-1, algorithm='elkan', n_init=3).fit(all_tweets_embedded)
predictions = kmeans.predict(all_tweets_embedded)
df['cluster'] = predictions
df.to_csv('tmp/clustering_attempt_{}_{}clusters.csv'.format(clustering_method, n))

# UMAP clustering - this is mostly for embedding down to n-dim space though
# logger.info("Attempting to cluster with UMAP")
# umap = umap.UMAP().fit_transform(all_tweets_embedded[0:10])


'''
from sklearn.cluster import DBSCAN

tiny_tweets = all_tweets_embedded[0:1000]
clustering = DBSCAN(eps=3, min_samples=100).fit(all_tweets_embedded[0:1000])
test = clustering.fit_predict(all_tweets_embedded[0:1000])
'''
# from sklearn.manifold import TSNE
# from matplotlib import pyplot as plt
# tsne = TSNE(n_components=2, verbose=0, perplexity=40, n_iter=300)
# tsne_pca_results = tsne.fit_transform(all_tweets_embedded)
# df['tsne-pca50-one'] = tsne_pca_results[:,0]
# df['tsne-pca50-two'] = tsne_pca_results[:,1]
# plt.figure(figsize=(16,4))
# plot = sns.scatterplot(
#     x="tsne-2d-one", y="tsne-2d-two",
#     #hue="y",
#     palette=sns.color_palette("hls", 10),
#     data=df,
#     legend="full",
#     alpha=0.3,
# )
# fig = plot.get_figure()
# fig.savefig('test.png')

# Look at samples from the cluster
# random.sample(list(df[df['cluster'] == 0]['text']), 10)
logger.info("Done")



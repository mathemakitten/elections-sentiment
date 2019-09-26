from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans, DBSCAN

from get_tweets import remove_tweets_by_user
from tf_hub_sentence_encoding import embed_tweets
from tweets_labeler import manual_map_cluster_to_category


def create_pseudo_label_tweets(unlabeled_data_file_path, remove_user, n_cluster, categories):
    unlabeled_tweets = _cluster_unlabeled_data(unlabeled_data_file_path, remove_user, n_cluster)
    labeled_tweets = _pseudo_label_data(unlabeled_tweets, categories)
    return labeled_tweets


def _cluster_data(unlabeled_data, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(unlabeled_data)
    predictions = kmeans.predict(unlabeled_data)
    return predictions


def _cluster_unlabeled_data(unlabeled_data_file_path, remove_user, n_cluster):
    unlabeled_tweets = pd.read_csv(unlabeled_data_file_path)
    unlabeled_tweets = remove_tweets_by_user(unlabeled_tweets, user=remove_user)

    tweet_to_embed = list(unlabeled_tweets['cleaned_text'])
    tweets_embedding = embed_tweets(tweet_to_embed)

    predictions = _cluster_data(tweets_embedding, n_cluster)
    unlabeled_tweets['cluster'] = predictions
    return unlabeled_tweets


def _pseudo_label_data(unlabeled_tweets, categories):
    manual_map = manual_map_cluster_to_category(unlabeled_tweets, categories)
    labeled_tweets = unlabeled_tweets.copy()
    labeled_tweets['label'] = labeled_tweets['cluster'].map(manual_map)

    _path = Path(unlabeled_data_file_path)
    file_parent_path, file_name = _path.parent, _path.name
    labeled_tweets.to_csv(str(file_parent_path/f'pseudo_labeled_{file_name}'), index=False)
    return labeled_tweets


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file-path', type=str, required=True)
    parser.add_argument('-ru', '--remove-user', type=str, required=True)
    parser.add_argument('-n', '--n-cluster', type=int, required=True)
    parser.add_argument('-c', '--categories', type=str, required=True)
    args = parser.parse_args()

    unlabeled_data_file_path = args.file_path
    remove_user = args.remove_user
    n_cluster = args.n_cluster
    categories = args.categories

    _ = create_pseudo_label_tweets(unlabeled_data_file_path, remove_user, n_cluster, categories)

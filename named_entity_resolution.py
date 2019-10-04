
from utils import get_logger, check_gpu
import pandas as pd
import glob
from data_prep import load_and_clean_data
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
import nltk
from data_prep import LEADER_USERNAMES
import pickle

logger = get_logger("NAMED-ENTITY")
df = load_and_clean_data()
logger.info("Data successfully loaded")

#df = df.head(1000)

# TODO NOTE TO SELF this has to be rerun for Oct!!!

# TODO English tweets only for NLP tasks

# Named entity recognition
tweet_tokenizer = TweetTokenizer(preserve_case=True, strip_handles=False, reduce_len=False)
detokenizer = TreebankWordDetokenizer()
entity_list = []

logger.info("Identifying named entities in tweets")
# TODO cache this -- just for dev, not prod -- it's an expensive op
entities_per_tweet = []
tweets_to_parse = [detokenizer.detokenize(tweet_tokenizer.tokenize(str(tweet))) for tweet in df['text']]
for i, tweet in enumerate(tweets_to_parse):
    if i % 10000 == 0:
        logger.info("Processing tweet {} of {}".format(i, len(tweets_to_parse)))
    tokens = nltk.word_tokenize(tweet)
    tagged = nltk.pos_tag(tokens)
    entities = nltk.chunk.ne_chunk(tagged)
    entities_extracted = [" ".join(w for w, t in elt) for elt in entities if isinstance(elt, nltk.Tree)]
    entity_list.extend((entities_extracted))
    entities_per_tweet.append(entities_extracted) # for joining back to the politician-level dataframe
    # TODO theoretically len(entity_list) == len(tweets_to_parse) so usernames can line up and we can match them up

df['named_entity'] = entities_per_tweet
df_politician = df[df['username'].isin(LEADER_USERNAMES)]
pickle.dump(df_politician, open('nlp_results/df_politician.pkl', 'wb'))

# Count most popular entities
popular_entities = pd.DataFrame(Counter(entity_list).most_common(25), columns=['entity', 'count'])

print(popular_entities)

# Dump onto disk for dashboard consumption

pickle.dump(entity_list, open('nlp_results/entity_list.pkl', 'wb'))
pickle.dump(popular_entities, open('nlp_results/named_entities.pkl', 'wb'))

# Can also do this at a politician level, ha --  "what does each one talk about the most?"
logger.info("Finished named entity detection")
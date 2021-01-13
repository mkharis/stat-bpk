import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import nltk
import string
import db
from textblob import TextBlob
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def show(title):
    st.title(title)

    lk = db.get_lk()
    lk_df = pd.DataFrame(lk, columns=['id', 'lk', 'bagian', 'tingkat'])

    with st.beta_expander('Choose Institution'):
        option_tingkat = st.selectbox('Choose Institution Level', lk_df['tingkat'].unique())
        option_lembaga = st.selectbox('Choose Institution', lk_df.loc[lk_df['tingkat'] == option_tingkat, 'lk'].tolist())
        id_lembaga = lk_df.loc[(lk_df['tingkat'] == option_tingkat) & (lk_df['lk'] == option_lembaga), 'id'].tolist()[0]

    twitter = db.get_twitter(str(id_lembaga))
    twitter_df = pd.DataFrame(twitter, columns=['id', 'time', 'description', 'source', 'target', 'tweets', 'usertweets', 'hashtags', 'location', 'retweets', 'likes', 'verified', 'following', 'followers', 'url'])

    if not twitter_df.empty:
        st.header('Tweets Preview')

        st.write(twitter_df)

        if st.button('Calculate Sentiment'):
            st.header('Sentiment')

            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')

            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')

            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            analyzer = SentimentIntensityAnalyzer()
            stopwords_id = nltk.corpus.stopwords.words('indonesian')

            twitter_df_clear = twitter_df[~twitter_df['tweets'].isna()]
            for idx in twitter_df_clear.index:
                twitter_df_clear.loc[idx, 'tweets'] = twitter_df_clear.loc[idx, 'tweets'].translate(str.maketrans('', '', string.punctuation)).lower()
                twitter_df_clear.loc[idx, 'tweets'] = ''.join(c for c in twitter_df_clear.loc[idx, 'tweets'] if 0 < ord(c) < 127)
                twitter_df_clear.loc[idx, 'tokenize'] = '|'.join(nltk.tokenize.word_tokenize(twitter_df_clear.loc[idx, 'tweets']))
                twitter_df_clear.loc[idx, 'filtered'] = '|'.join([t for t in twitter_df_clear.loc[idx, 'tokenize'].split('|') if t not in stopwords_id])
                twitter_df_clear.loc[idx, 'stemmed'] = stemmer.stem(twitter_df_clear.loc[idx, 'filtered'].replace('|', ' '))
                try:
                    twitter_df_clear.loc[idx, 'blob'] = str(TextBlob(twitter_df_clear.loc[idx, 'stemmed']).translate(to='en'))
                except:
                    twitter_df_clear.loc[idx, 'blob'] = twitter_df_clear.loc[idx, 'stemmed']
                polarity = analyzer.polarity_scores(twitter_df_clear.loc[idx, 'blob'])
                twitter_df_clear.loc[idx, 'polarity_pos'] = polarity['pos']
                twitter_df_clear.loc[idx, 'polarity_neg'] = polarity['neg']
                twitter_df_clear.loc[idx, 'polarity_neu'] = polarity['neu']
                sentiment = np.argmax([polarity['pos'], polarity['neg'], polarity['neu']]) + 1
                if sentiment == 1:
                    twitter_df_clear.loc[idx, 'sentiment'] = 'Positive'
                if sentiment == 2:
                    twitter_df_clear.loc[idx, 'sentiment'] = 'Negative'
                if sentiment == 3:
                    twitter_df_clear.loc[idx, 'sentiment'] = 'Neutral'

            twitter_pie = px.pie(twitter_df_clear, names='sentiment', labels={'sentiment': 'Sentiment'},template='simple_white')
            st.plotly_chart(twitter_pie, use_container_width=True)

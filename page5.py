import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import pyLDAvis
import pyLDAvis.sklearn
import db
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

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
        st.header('Top 10 Most Topic Related')

        n_topics = 10
        top_topics = 10
        top_words = 10
        max_df = 0.95
        min_df = 2

        tweets = twitter_df.loc[~twitter_df['tweets'].isna(), 'tweets'].apply(lambda x: x.strip())

        count_vector = CountVectorizer(lowercase=True, token_pattern=r'\b[a-zA-Z]{3,}\b', max_df=max_df, min_df=min_df)
        dtm_tf = count_vector.fit_transform(tweets)
        tf_terms = count_vector.get_feature_names()

        lda_tf = LatentDirichletAllocation(n_components=n_topics, learning_method='online', random_state=0).fit(dtm_tf)

        vsm_topics = lda_tf.transform(dtm_tf)
        doc_topic = np.array([d.argmax() + 1 for d in vsm_topics])

        st.write('In total there are {} major topics, distributed as follows'.format(len(set(doc_topic))))
        topic_histogram = px.histogram(pd.DataFrame({'topic': doc_topic}), x='topic', template='simple_white')
        st.plotly_chart(topic_histogram, use_container_width=True)

        st.write('Printing top {} topics, with top {} words:'.format(top_topics, top_words))
        for topic_idx, topic in enumerate(lda_tf.components_[:top_topics]):
            st.write('Topic {}:'.format(topic_idx + 1))
            st.write(' '.join([tf_terms[i] for i in topic.argsort()[:-top_words - 1:-1]]))

        st.header('Topic Model Visualization')

        st.components.v1.html(pyLDAvis.prepared_data_to_html(pyLDAvis.sklearn.prepare(lda_tf, dtm_tf, count_vector)), width=800, height=800, scrolling=True)

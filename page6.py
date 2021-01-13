import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import networkx as nx
import db

def set_node_community(g, communities_modularity):
    for c, v_c in enumerate(communities_modularity):
        for v in v_c:
            g.nodes[v]['community'] = c + 1

def get_color(i, r_off=1, g_off=1, b_off=1):
     r0, g0, b0 = 0, 0, 0
     n = 16
     low, high = 0.1, 0.9
     span = high - low
     r = low + span * (((i + r_off) * 3) % n) / (n - 1)
     g = low + span * (((i + g_off) * 5) % n) / (n - 1)
     b = low + span * (((i + b_off) * 7) % n) / (n - 1)
     return (r, g, b)

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
        st.header('Social Network')

        twitter_network_df = twitter_df[['source', 'target']]
        twitter_network_df.dropna(inplace=True)

        g = nx.from_pandas_edgelist(twitter_network_df)

        st.subheader('Network Graph')
        fig1, _ = plt.subplots(figsize=(10, 10))
        nx.draw(g, with_labels=True, node_color='skyblue', node_size=1000, arrowstyle='->', arrowsize=20, edge_color='r', font_size=9, pos=nx.kamada_kawai_layout(g))
        st.pyplot(fig1, use_container_width=True)

        communities_modularity = sorted(nx.algorithms.community.greedy_modularity_communities(g), key=len, reverse=True)
        community = set_node_community(g, communities_modularity)

        node_color = [get_color(g.nodes[v]['community']) for v in g.nodes]

        st.subheader('Network Community Graph')
        fig2, _ = plt.subplots(figsize=(10, 10))
        nx.draw(g, with_labels=True, node_color=node_color, node_size=1000, arrowstyle='->', arrowsize=20, edge_color='r', font_size=9, pos=nx.kamada_kawai_layout(g))
        st.pyplot(fig2, use_container_width=True)

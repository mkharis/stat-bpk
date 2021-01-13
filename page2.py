import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import db

def show(title):
    st.title(title)

    lk = db.get_lk()
    lk_df = pd.DataFrame(lk, columns=['id', 'lk', 'bagian', 'tingkat'])

    masalah = db.get_masalah()
    masalah_df = pd.DataFrame(masalah, columns=['id', 'masalah', 'jenis', 'tingkat'])

    masalah_dengan_nilai = db.get_masalah_dengan_nilai()
    masalah_dengan_nilai_df = pd.DataFrame(masalah_dengan_nilai, columns=['id', 'masalah', 'jenis', 'tingkat'])

    st.header('Institution and Problem')

    with st.beta_expander('Choose Institutions'):
        option_tingkat = st.selectbox('Choose Institutions Level', lk_df['tingkat'].unique())
        option_lembagas = st.multiselect('Choose Institutions', lk_df.loc[lk_df['tingkat'] == option_tingkat, 'lk'].tolist())
        id_lembagas = lk_df.loc[(lk_df['tingkat'] == option_tingkat) & (lk_df['lk'].isin(option_lembagas)), 'id'].tolist()

    with st.beta_expander('Choose Problem'):
        option_utama = st.selectbox('Choose Main Problem', ('Permasalahan Kelemahan Sistem Pengendalian Intern', 'Permasalahan Ketidakpatuhan terhadap Ketentuan Peraturan Perundang-undangan'))
        if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_df.loc[masalah_df['tingkat'] == option_tingkat, 'jenis'].unique())
        else:
            option_jenis = st.selectbox('Choose Kind of Problem', masalah_dengan_nilai_df.loc[masalah_dengan_nilai_df['tingkat'] == option_tingkat, 'jenis'].unique())

    if option_utama == 'Permasalahan Kelemahan Sistem Pengendalian Intern':
        temuan_dfs = pd.DataFrame()
        for id_lembaga, option_lembaga in zip(id_lembagas, option_lembagas):
            temuan = db.get_temuan_by_lk_only(str(id_lembaga))
            temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'tahun', 'semester', 'masalah', 'jenis'])
            temuan_df = temuan_df[temuan_df['jenis'] == option_jenis]
            temuan_df = temuan_df.groupby(['tahun', 'semester']).sum().reset_index()
            temuan_df.loc[:, 'lk'] = option_lembaga
            temuan_dfs = temuan_dfs.append(temuan_df, ignore_index=True)

        st.header('Comparison Between Institutions')

        if len(option_lembagas) != 0:
            st.subheader('Number of Problems \'{}\' in Several Institutions'.format(option_jenis))
            temuan_dfs.loc[:, 'tahun_semester'] = temuan_dfs[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)
            temuan_bar = px.bar(temuan_dfs, x='jumlah', y='lk', color='tahun_semester', labels={'lk': 'Institution', 'jumlah': 'Number of Problems', 'tahun_semester': 'Year Semester'}, template='simple_white')
            st.plotly_chart(temuan_bar, use_container_width=True)

            st.markdown('The graph above presents the problem \'{}\' in {}.\n\nThere are {} institutions on this graph: {}.\n\nThe highest number of problems was achieved by {} ({}).\n\nThen, the lowest was achieved by {} ({}).\n\nThe difference between the highest and lowest is {}; while the average number of problems is {}.\n\nIn more detail, it means {} has the problem \'{}\' that tend to dominate.\n\nSo, it needs to be taken into consideration in policy making by the government.'.format(option_jenis, str(temuan_dfs['tahun'].min()) + '-' + str(temuan_dfs['tahun'].max()), len(option_lembagas), ', '.join(option_lembagas), temuan_dfs.groupby('lk').sum()['jumlah'].idxmax(), temuan_dfs.groupby('lk').sum()['jumlah'].max(), temuan_dfs.groupby('lk').sum()['jumlah'].idxmin(), temuan_dfs.groupby('lk').sum()['jumlah'].min(), temuan_dfs.groupby('lk').sum()['jumlah'].max() - temuan_dfs.groupby('lk').sum()['jumlah'].min(), str(temuan_dfs.groupby('lk').sum()['jumlah'].mean()).replace('.', ','), temuan_dfs.groupby('lk').sum()['jumlah'].idxmax(), option_jenis))

    else:
        temuan_dfs = pd.DataFrame()
        for id_lembaga, option_lembaga in zip(id_lembagas, option_lembagas):
            temuan = db.get_temuan_dengan_nilai_by_lk_only(str(id_lembaga))
            temuan_df = pd.DataFrame(temuan, columns=['jumlah', 'nilai', 'tahun', 'semester', 'masalah', 'jenis'])
            temuan_df = temuan_df[temuan_df['jenis'] == option_jenis]
            temuan_df = temuan_df.groupby(['tahun', 'semester']).sum().reset_index()
            temuan_df.loc[:, 'lk'] = option_lembaga
            temuan_dfs = temuan_dfs.append(temuan_df, ignore_index=True)

        st.header('Comparison Between Institutions')

        if len(option_lembagas) != 0:
            st.subheader('Number of Problems \'{}\' in Several Institutions'.format(option_jenis))
            temuan_dfs.loc[:, 'tahun_semester'] = temuan_dfs[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)
            temuan_bar = px.bar(temuan_dfs, x='jumlah', y='lk', color='tahun_semester', labels={'lk': 'Institution', 'jumlah': 'Number of Problems', 'tahun_semester': 'Year Semester'}, template='simple_white')
            st.plotly_chart(temuan_bar, use_container_width=True)

            st.markdown('The graph above presents the problem \'{}\' in {}.\n\nThere are {} institutions on this graph: {}.\n\nThe highest number of problems was achieved by {} ({}).\n\nThen, the lowest was achieved by {} ({}).\n\nThe difference between the highest and lowest is {}; while the average number of problems is {}.\n\nIn more detail, it means {} has the problem \'{}\' that tend to dominate.\n\nSo, it needs to be taken into consideration in policy making by the government.'.format(option_jenis, str(temuan_dfs['tahun'].min()) + '-' + str(temuan_dfs['tahun'].max()), len(option_lembagas), ', '.join(option_lembagas), temuan_dfs.groupby('lk').sum()['jumlah'].idxmax(), temuan_dfs.groupby('lk').sum()['jumlah'].max(), temuan_dfs.groupby('lk').sum()['jumlah'].idxmin(), temuan_dfs.groupby('lk').sum()['jumlah'].min(), temuan_dfs.groupby('lk').sum()['jumlah'].max() - temuan_dfs.groupby('lk').sum()['jumlah'].min(), str(temuan_dfs.groupby('lk').sum()['jumlah'].mean()).replace('.', ','), temuan_dfs.groupby('lk').sum()['jumlah'].idxmax(), option_jenis))

            st.subheader('Amount of Loss \'{}\' in Several Institutions'.format(option_jenis))
            temuan_dfs.loc[:, 'tahun_semester'] = temuan_dfs[['tahun', 'semester']].apply(lambda x: '{}S{}'.format(x[0], x[1]), axis=1)
            temuan_bar = px.bar(temuan_dfs, x='nilai', y='lk', color='tahun_semester', labels={'lk': 'Institution', 'nilai': 'Amount of Loss (Million Rp)', 'tahun_semester': 'Year Semester'}, template='simple_white')
            st.plotly_chart(temuan_bar, use_container_width=True)

            st.markdown('The graph above presents the problem \'{}\' in {}.\n\nThere are {} institutions on this graph: {}.\n\nThe highest amount of loss was achieved by {} ({} million rupiah).\n\nThen, the lowest was achieved by {} ({} million rupiah).\n\nThe difference between the highest and lowest is {} million rupiah; while the average amount of loss is {} million rupiah.\n\nIn more detail, it means {} has the problem \'{}\' that tend to dominate.\n\nSo, it needs to be taken into consideration in policy making by the government.'.format(option_jenis, str(temuan_dfs['tahun'].min()) + '-' + str(temuan_dfs['tahun'].max()), len(option_lembagas), ', '.join(option_lembagas), temuan_dfs.groupby('lk').sum()['nilai'].idxmax(), str(temuan_dfs.groupby('lk').sum()['nilai'].max()).replace('.', ','), temuan_dfs.groupby('lk').sum()['nilai'].idxmin(), str(temuan_dfs.groupby('lk').sum()['nilai'].min()).replace('.', ','), str(temuan_dfs.groupby('lk').sum()['nilai'].max() - temuan_dfs.groupby('lk').sum()['nilai'].min()).replace('.', ','), str(temuan_dfs.groupby('lk').sum()['nilai'].mean()).replace('.', ','), temuan_dfs.groupby('lk').sum()['nilai'].idxmax(), option_jenis))
